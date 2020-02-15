# coding: utf-8

"""
Database utilities.
"""

import contextlib
import enum
import functools
import logging
import os
import six
import threading
import traceback

from sqlalchemy.engine import create_engine
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import defer as _defer, noload, scoped_session, sessionmaker
from sqlalchemy.orm.attributes import InstrumentedAttribute
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.sql import ClauseElement
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy_mixins import ReprMixin, SmartQueryMixin


Base = declarative_base()


class BaseModel(Base, SmartQueryMixin, ReprMixin):
    """
    Abstract base class for SQLAlchemy models.
    """
    __abstract__ = True
    __repr__ = ReprMixin.__repr__
    __repr_max_length__ = float('inf')

    subclasses_map = {}

    @property
    def pks(self):
        """
        :rtype: typing.Dict[str, Any]
        """
        return dict(zip(self.pk_names, self.pk_values))


class NotFound(Exception):
    pass


class Locked(Exception):
    pass


class Timeout(Exception):
    pass


# `sqlalchemy.exc.OperationalError` arguments when raised because of user requested query cancellation.
TIMEOUT_EXCEPTION_ARGS = ('(psycopg2.extensions.QueryCanceledError) canceling statement due to user request\n',)

LOGGER = logging.getLogger('martylib.db_utils')

_PREPARED = False
_READ_ONLY_SUPPORT = bool(os.environ.get('ENABLE_RO_DB', False))
_NO_AUTOFLUSH = bool(os.environ.get('SQLALCHEMY_DISABLE_AUTOFLUSH', False))
DB_URL_PROD = os.environ.get('DB_URL')
DB_URL_TEST = os.environ.get('DB_URL_TEST')

if not _READ_ONLY_SUPPORT:
    # Can't use logs here, since this module is imported before logging is configured.
    print('WARNING: read-only database replicas support is disabled (ENABLE_RO_DB)')

Engine = None
Session = None
ReadOnlyEngine = None


class IsolationLevel(enum.Enum):
    READ_COMMITTED = 'READ COMMITTED'
    READ_UNCOMMITTED = 'READ UNCOMMITTED'
    REPEATABLE_READ = 'REPEATABLE READ'
    SERIALIZABLE = 'SERIALIZABLE'
    AUTOCOMMIT = 'AUTOCOMMIT'


def prepare_engine(read_only=False, echo=False):
    url = DB_URL_PROD
    if url is None:
        url = 'sqlite://'
    elif read_only:
        if 'rw.db.yandex.net' in url:
            url = url.replace('rw.db.yandex.net', 'ro.db.yandex.net')
        elif 'target_session_attrs=' in url:
            url = url.replace('target_session_attrs=read-write', 'target_session_attrs=any')
        else:
            url = '{}_ro_local'.format(url)
    if 'sqlite' in url:
        return create_engine(url, echo=echo)
    return create_engine(url, echo=echo, pool_size=30, max_overflow=30)


class CustomSessionFactory(sessionmaker):
    def __init__(self, *args, **kwargs):
        super(CustomSessionFactory, self).__init__(*args, **kwargs)

    # noinspection PyTypeChecker
    def __call__(self, **local_kw):
        # Mostly copy-pasted from `sessionmaker`.
        for k, v in self.kw.items():
            if k == 'info' and 'info' in local_kw:
                d = v.copy()
                d.update(local_kw['info'])
                local_kw['info'] = d
            else:
                local_kw.setdefault(k, v)

        return self.class_(**local_kw)


def _get_session_ident():
    """
    Returns session identification for `scoped_session` - read-only flag and current thread identification.
    Only checks for `Storage().read_only_db` if `ENABLE_RO_DB` environment variable is set to True.
    """
    return threading.current_thread().ident


def prepare_module(autoflush=None, echo=False, **kwargs):
    """
    Configures DB engine and BaseModel sessions.
    """
    global _PREPARED

    if autoflush is None:
        autoflush = not _NO_AUTOFLUSH

    if not _PREPARED:
        global Engine
        global ReadOnlyEngine
        global Session

        Engine = prepare_engine(echo=echo)
        ReadOnlyEngine = prepare_engine(read_only=True, echo=echo)

        Session = scoped_session(CustomSessionFactory(bind=Engine, autoflush=autoflush, **kwargs), _get_session_ident)

        BaseModel.set_session(Session)  # Use read-write session by default in order to `<Model>.query` to work properly.
        _PREPARED = True


def shutdown_module():
    """
    Disposes prepared DB engine and stuff
    """

    global _PREPARED

    if _PREPARED:
        global Engine
        global ReadOnlyEngine
        global Session

        Engine.dispose()
        ReadOnlyEngine.dispose()

        Engine = None
        ReadOnlyEngine = None
        Session = None

        _PREPARED = False


def _cancel_request(session):
    try:
        session.connection().connection.cancel()
    except OperationalError:
        raise Timeout


def log_pg_stat_activity():
    # https://habr.com/ru/company/wargaming/blog/323354/
    debug_connection = Engine.connect()
    for process in debug_connection.execute('SELECT pid, application_name, state, query FROM pg_stat_activity;').fetchall():
        LOGGER.info(process)


@contextlib.contextmanager
def session_scope(
    timeout=None,
    statement_timeout=None,
    lock_timeout=None,
    interruption_log_level=logging.WARNING,
    isolation_level=None,
    nested=False,
    application_name=None,
):
    """
    Provides a transactional scope around a series of operations.

    If :param:`timeout` is set, cancellation request will be send after :param:`timeout` seconds.

    :param title: trace title (see `search.martylib.trace`)
    :param timeout: application level timeout in seconds
    :param statement_timeout: statement timeout for session in seconds (https://www.postgresql.org/docs/9.4/static/runtime-config-client.html)
    :param lock_timeout: lock timeout for session in seconds (https://www.postgresql.org/docs/9.4/static/runtime-config-client.html)
    :param interruption_log_level: logging level to use to log exceptions raised during session
    :param isolation_level: transaction isolation level (database default used if None)
    :param nested: if True, new session is created; otherwise the same session is used
    :param application_name: used for `SET application_name` if not None
    """
    prepare_module()

    timer = None

    if nested:
        Session.remove()

    session = BaseModel.session()

    try:
        if statement_timeout is not None and lock_timeout is not None:
            if lock_timeout > statement_timeout:
                LOGGER.warning('lock_timeout greater than statement_timeout is pointless')

        if statement_timeout is not None:
            session.execute('SET SESSION statement_timeout = {};'.format(int(statement_timeout * 1000)))

        if lock_timeout is not None:
            session.execute('SET SESSION lock_timeout = {};'.format(int(lock_timeout * 1000)))

        if isolation_level is not None:
            session.connection(execution_options=dict(isolation_level=isolation_level.value))

        if timeout is not None:
            timer = threading.Timer(timeout, lambda: _cancel_request(session))
            timer.start()

        if application_name is None:
            caller = traceback.extract_stack()[-3]
            application_name = '{}:{}'.format(caller[0], caller[1])

        session.execute("SET application_name = '{}';".format(six.moves.urllib_parse.quote(application_name)))

        yield session
        session.commit()

    except Exception as e:
        formatted_exception = str(e)

        LOGGER.log(interruption_log_level, 'session interrupted by %s', e)
        session.rollback()

        if 'deadlock' in formatted_exception:
            log_pg_stat_activity()

        if isinstance(e, OperationalError) and e.args == TIMEOUT_EXCEPTION_ARGS:
            raise Timeout()

        raise

    finally:
        if timer:
            timer.cancel()

        session.close()


nested_session_scope = functools.partial(session_scope, nested=True)


def prepare_db():
    """
    Creates necessary database structure.
    """
    prepare_module()

    try:
        LOGGER.info('preparing everything: %s', Engine)
        BaseModel.metadata.create_all(Engine)
    except Exception as e:
        LOGGER.exception('failed to prepare database: %s: %s', Engine, e)
        raise


def clear_db(echo=False):
    """
    Clear all the data and schema from DB
    """
    engine = prepare_engine(echo=echo)
    LOGGER.warning('dropping everything: %s', engine)
    if engine.name == 'sqlite':
        # shutdown module, effectively dropping in-memory DB
        shutdown_module()
    else:
        engine.execute('drop schema if exists public cascade')
        engine.execute('create schema public')


def get_or_create(session, model_type, **kwargs):
    instance = session.query(model_type).filter_by(**kwargs).first()
    if instance:
        return instance, False
    else:
        params = dict((k, v) for k, v in kwargs.items() if not isinstance(v, ClauseElement))
        # noinspection PyArgumentList
        instance = model_type(**params)
        session.add(instance)
        return instance, True


def list_models(
    model_type, collection_type, limit=100, offset=0, page=1, disable_limiting=False, order=None,
    shallow=False, shallow_fields=None, exclude=None, defer=None, **kwargs
):
    """
    Queries given :param:`model_type`, converts each model to corresponding protobuf message and puts result into
    :param:`collection_type` container.

    :param model_type
    :param collection_type: protobuf container for a list of messages converted from models
    :param limit
    :param offset
    :param page
    :param disable_limiting: completely disables limiting (shockingly), use with caution
    :param order
    :param shallow: whether to exclude fields from query (using `noload`)
    :param shallow_fields: list of fields to exclude from query (using `noload`) if :param:`shallow` is set to True
    :param exclude: fields to exclude from protobuf conversion
    :param defer: model fields to defer (not loaded until explicitly queried)
    """
    shallow_fields = shallow_fields or ()
    exclude = exclude or ()
    defer = defer or ()

    with session_scope():
        collection = collection_type()

        if kwargs:
            # Only apply SmartQuery filters if they are actually set, e.g. ignore empty lists/strings.
            qs = model_type.where(**{
                k: v
                for k, v in kwargs.items()
                if v or v is False or v is None
            })
        else:
            qs = model_type.where()

        if shallow:
            for f in shallow_fields:
                qs = qs.options(noload(f))

        if defer:
            # noinspection PyCallingNonCallable
            qs = qs.options(_defer(*defer))

        if order is not None:
            qs = qs.order_by(order)

        if not disable_limiting:
            if page <= 0:
                raise ValueError('page should be greater than zero, got {}'.format(page))

            if page != 1:
                offset = limit * (page - 1)

            qs = qs.limit(limit).offset(offset)

        collection.objects.extend((model.to_protobuf(exclude=exclude) for model in qs.all()))
        return collection


def retrieve_model(model_type, pk, shallow=False, shallow_fields=None):
    with session_scope() as session:
        qs = session.query(model_type)

        if shallow:
            for f in shallow_fields:
                qs = qs.options(noload(f))

        model = qs.get(pk)
        if model is None:
            raise NotFound(pk)

        return model.to_protobuf()


def delete_model(model_type, **identification):
    with session_scope() as session:
        try:
            beta = model_type.where(**identification).one()
            session.delete(beta)
        except NoResultFound:
            pass

    return


def _lock_one(model_type, nowait=False, exc_type=Locked, **identification):
    # `noload` is required to eliminate DISTINCT clauses.
    try:
        return model_type.where(**identification).options(noload('*')).with_for_update(nowait=nowait).one()
    except NoResultFound:
        raise NotFound(identification)
    except OperationalError:
        raise exc_type('{}.where(**{}) is already locked'.format(model_type, identification))


@contextlib.contextmanager
def lock_one(model_type, nowait=False, exc_type=Locked, scoped=True, **identification):
    """
    Locks one model in database.
    """
    if scoped:
        with session_scope():
            yield _lock_one(model_type=model_type, nowait=nowait, exc_type=exc_type, **identification)
    else:
        yield _lock_one(model_type=model_type, nowait=nowait, exc_type=exc_type, **identification)


@contextlib.contextmanager
def lock_model(session, model_type, nowait=True, exc_type=Locked, options=(), filters=()):
    # `noload` is required to eliminate DISTINCT clauses.
    try:
        yield (
            session.query(model_type)
            .filter(*filters)
            .options(*options)
            .options(noload('*'))
            .with_for_update(nowait=nowait)
            .one()
        )
    except NoResultFound:
        raise NotFound(model_type, filters)
    except OperationalError:
        raise exc_type(model_type, filters)


@contextlib.contextmanager
def lock_by_query(query, nowait=True, exc_type=Locked, first=False):
    # `noload` is required to eliminate DISTINCT clauses.
    try:
        query = (
            query
            .options(noload('*'))
            .with_for_update(nowait=nowait)
        )

        if first:
            query_result = query.first()
            if not query_result:
                raise NotFound()

            yield query_result

        else:
            yield query.one()

    except NoResultFound:
        raise NotFound()
    except OperationalError:
        raise exc_type()


@contextlib.contextmanager
def lock_models(session, model_type, nowait=True, exc_type=Locked, options=(), filters=()):
    # `noload` is required to eliminate DISTINCT clauses.
    try:
        yield (
            session.query(model_type)
            .filter(*filters)
            .options(*options)
            .options(noload('*'))
            .with_for_update(nowait=nowait)
            .all()
        )
    except OperationalError:
        raise exc_type(model_type, filters)


def model_class(message):
    return BaseModel.subclasses_map[type(message)]


def _convert_field(f):
    if isinstance(f, InstrumentedAttribute):
        return f.key
    elif isinstance(f, enum.Enum):
        return f.name
    elif isinstance(f, six.string_types):
        return f
    raise ValueError('unsupported field type: %s', type(f))


def generate_field_name(*path):
    """
    Joins field names with '.'.
    Supports `InstrumentedAttribute`, `Fields` and `str`.
    """
    # noinspection PyUnresolvedReferences
    return '.'.join((_convert_field(field) for field in path))

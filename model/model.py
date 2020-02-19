import sqlalchemy
from sqlalchemy import types

from src.utils.db_utils import BaseModel


class Server(BaseModel):
    __tablename__ = 'ctf__Server'

    hostname = sqlalchemy.Column(types.TEXT, primary_key=True)
    ip = sqlalchemy.Column(types.TEXT, index=True)
    uptime = sqlalchemy.Column(types.TEXT)
    state = sqlalchemy.Column(types.TEXT)
    last_pinged = sqlalchemy.Column(types.JSON)
    num_state = sqlalchemy.Column(types.INT)


class Team(BaseModel):
    __tablename__ = 'ctf__Team'

    name = sqlalchemy.Column(types.TEXT, primary_key=True)
    server_hijacked = sqlalchemy.Column(types.INT)
    score = sqlalchemy.Column(types.INT)
    contact = sqlalchemy.Column(types.TEXT)
    register_time = sqlalchemy.Column(types.FLOAT)
    flags_passed = sqlalchemy.Column(types.INT)
    secret_key = sqlalchemy.Column(types.TEXT)


class Log(BaseModel):
    __tablename__ = 'ctf__Log'

    time = sqlalchemy.Column(types.INT, primary_key=True)
    message = sqlalchemy.Column(types.TEXT)

import sqlalchemy
from sqlalchemy import types

from src.utils.db_utils import BaseModel


class Server(BaseModel):
    __tablename__ = 'ctf__Server'

    hostname = sqlalchemy.Column(types.TEXT, primary_key=True)
    ip = sqlalchemy.Column(types.TEXT)
    uptime = sqlalchemy.Column(types.TEXT)
    state = sqlalchemy.Column(types.TEXT)


class Team(BaseModel):
    __tablename__ = 'ctf__Team'

    name = sqlalchemy.Column(types.TEXT, primary_key=True)
    server_hijacked = sqlalchemy.Column(types.INT)
    score = sqlalchemy.Column(types.INT)
    contact = sqlalchemy.Column(types.TEXT)
    register_time = sqlalchemy.Column(types.FLOAT)

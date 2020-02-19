import enum
import time
import struct
import io
import base64
import requests
from flask import Flask, render_template, request, redirect, jsonify, abort
from src.utils.db_utils import session_scope, prepare_db
from model import model


class ServerState(enum.IntEnum):
    NOT_CAPTURED = 0
    FIGHT = 1
    CAPTURED = 2
    UNAVAILABLE = 3
    INVISIBLE = 4


app = Flask(__name__)


# @app.route('/')
# def index():
#     # return render_template("index.html")
#     # return render_template("stub.html")
#     return render_template("register.html")
#


SALT = b"E\xe0\xda\xfa\x8b<\xa3E\x9fA\x88\x01~}\x90\x90\x9f\xbdM\xd3R\x03\xb9\x83\x96\xd6I\x9c\x17\x1a\xa2\xb6\x07" \
       b"\xc9\x83j\xa6t\x08\x0e\x18(`\x88\xbe\xc9*g\x8fW_\xe3\xab\xe2\xff\xa4*E\xablB\xa4\x12\x14\xe3e\xbep\x8bP\xf7" \
       b"\x0b\xb8\xe6\xba&d\x82\xb7M\xff\x9c\xc1\x063^\xc0\xf2.\xb4PK\xaf\xb4\xe5'c\x15\xfc\xfb7x\xff\xdf\xe8\xcc,J" \
       b"\x1a>\xd8Ld0\x91}\x95:\xf3\x1f\xa4\xfc,\xba/iD\x8b9\xca\x15\xb3\xb2\xc8Out\xabF\x96\xa7\xb6D'\x99\x0f0\x16" \
       b"\xf2\x97\x8cQ\xc4\x91\xe7\xc96\xea\x99V}/\x0b\xd7%\x04x\xe3\xe4\x8e{\xdd>\xc5\x97N\x17~N^\xc7\tRq\xa2\xfame[" \
       b"\x08v\x1d\xec\xed\xee$\xd5}u\x84\xfa\x9f\x8b\xf7\xbf\xe0\x84\x13\xf7\xc9\xf6\xf0^\x04\xfa\xed\xb1\xbfN\x9dFH" \
       b"\xa3\xc5a\x10\xc1\xc5TcTU\xfe\x16\xd5'\xae\xb5\x02F[\xf6\x82\xba\xbf\xe4\xd3P\x13\x0b\xc2\x05\x1c\x988"


def get_team(session, req) -> model.Team:
    data = io.BytesIO(base64.b64decode(req['data']))
    name_len = struct.unpack('I', data.read(4))[0]
    name = bytes(x ^ y for x, y in zip(data.read(name_len), SALT[name_len])).decode()
    return session.query(model.Team).filter(model.Team.name == name).first()


@app.route("/", methods=["POST", "GET"])
def register():
    if request.method == "GET":
        return render_template("register.html", message='')
    elif request.method == "POST":
        with session_scope() as session:
            team_name = request.form["team"]
            team_fb = request.form["feedback"]

            if session.query(model.Team).filter(model.Team.name == team_name).first() is None:
                session.merge(
                    model.Team(
                        name=team_name,
                        contact=team_fb,
                        register_time=time.time(),
                    )
                )
                return render_template("register.html", message='Регистрация прошла успешно! Мы свяжемся с вами!')
            return render_template("register.html", message='Упс, команда с таким именем уже есть...')


@app.route('/сервера')
def server_state():
    servers = [
        {
            "hostname": "engaged-octopus",
            "ip": "1.1.1.1",
            "uptime": "1h56m",
            "state": "captured by K.G.B.",
            "num_state": ServerState.CAPTURED
        },
        {
            "hostname": "sad-cat",
            "ip": "1.2.1.2",
            "uptime": "2h6m",
            "state": "fight between K.G.B & grumpy walruses",
            "num_state": ServerState.FIGHT
        },
        {
            "hostname": "playful-lion",
            "ip": "2.2.2.2",
            "uptime": "server is down",
            "state": "unavailable",
            "num_state": ServerState.UNAVAILABLE
        },
        {
            "hostname": "pride-penguin",
            "ip": "6.0.6.0",
            "uptime": "1d6h3m",
            "state": "working properly",
            "num_state": ServerState.NOT_CAPTURED
        }
    ]

    coloration = []
    for ind, val in enumerate(servers):
        if val['num_state'] == ServerState.FIGHT:
            coloration.insert(ind, "has-background-danger")
        elif val["num_state"] == ServerState.CAPTURED:
            coloration.insert(ind, "has-background-warning")
        elif val["num_state"] == ServerState.UNAVAILABLE:
            coloration.insert(ind, "has-background-grey-lighter")

    return render_template("servers.html", servers=enumerate(servers), coloration=coloration)


@app.route('/таблица')
def table():
    with session_scope() as session:
        result = (
            session.query(model.Team)
            .order_by(model.Team.score.desc())
            .all()
        )
        return render_template("table.html", result=enumerate(result))


@app.route('/процесс', methods=['POST'])
def process():
    with session_scope() as session:
        server = (
            session.query(model.Server)
            .filter(
                model.Server.ip == request.remote_addr
            )
            .first()
        )
        if not server:
            return jsonify({'error': 'Bad ip!'})

        if server.num_state == 4:
            return jsonify({'error': 'Your server dose not ready. You have 30 minutes to prepare'})

        if server.last_pinged is None:
            server.last_pinged = {}

        try:
            team = get_team(session, request.json)
        except Exception as e:
            return jsonify({'error': str(e)})

        state = server.last_pinged.get(team.name, [0., 0])  # last_pinged, ban

        if state[1]:
            if time.time() - state[0] < 10 * 60:
                return jsonify({'error': 'There were some errors before! Wait for 10 minutes!'})
            state[1] = 0

        if time.time() - state[0] < 5:
            state[1] = 1
            return jsonify({'error': 'Too many requests! Wait for 10 minutes!'})

        for team_name, value in server.last_pinged:
            if team_name != team.name and time.time() - value[0] < 10 * 60:
                value[1] = 1
                state[1] = 1
                return jsonify({'error': f'Conflict with team {team_name}! Wait for 10 minutes!'})

        key = requests.get(f'http://{server.ip}:{request.json["port"]}')
        if key.content != team.secret_key:
            abort(413)

        state[0] = time.time()

        team.score += 90 / (864000 // 5) / session.query(model.Team).count()
        session.query(model.Server).update({'last_pinged': server.last_pinged})


prepare_db()

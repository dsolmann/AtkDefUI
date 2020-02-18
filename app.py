import enum
import time
from flask import Flask, render_template, request, redirect
from src.utils.db_utils import session_scope, prepare_db
from model import model


class ServerState(enum.IntEnum):
    NOT_CAPTURED = 0
    FIGHT = 1
    CAPTURED = 2
    UNAVAILABLE = 3


app = Flask(__name__)


# @app.route('/')
# def index():
#     # return render_template("index.html")
#     # return render_template("stub.html")
#     return render_template("register.html")
#

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


@app.route('/servers')
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


@app.route('/table')
def table():
    with session_scope() as session:
        result = (
            session.query(model.Team)
            .order_by(model.Team.score.desc())
            .all()
        )
        return render_template("table.html", result=enumerate(result))


if __name__ == '__main__':
    prepare_db()
    app.run(host='0.0.0.0', port=80)

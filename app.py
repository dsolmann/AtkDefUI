from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)


@app.route('/')
def index():
    return render_template("index.html")


@app.route("/register", methods=["POST", "GET"])
def register():
    if request.method == "GET":
        return render_template("register.html")
    elif request.method == "POST":
        team_name = request.form["team"]
        team_fb = request.form["feedback"]
        print(team_name, team_fb)  # Replace with needed API
        return redirect("/servers")


@app.route('/servers')
def server_state():
    """
    Num States:
    0. Uncaptured
    1. Fight
    2. Captured
    3. Unavailable
    """
    servers = [
        {
            "hostname": "engaged-octopus",
            "ip": "1.1.1.1",
            "uptime": "1h56m",
            "state": "captured by K.G.B.",
            "num_state": 2
        },
        {
            "hostname": "sad-cat",
            "ip": "1.2.1.2",
            "uptime": "2h6m",
            "state": "fight between K.G.B & grumpy walruses",
            "num_state": 1
        },
        {
            "hostname": "playful-lion",
            "ip": "2.2.2.2",
            "uptime": "server is down",
            "state": "unavailable",
            "num_state": 3
        },
        {
            "hostname": "pride-penguin",
            "ip": "6.0.6.0",
            "uptime": "1d6h3m",
            "state": "working properly",
            "num_state": 0
        }
    ]

    coloration = []
    for ind, val in enumerate(servers):
        if val['num_state'] == 2:
            coloration.insert(ind, "has-background-danger")
        elif val["num_state"] == 1:
            coloration.insert(ind, "has-background-warning")
        elif val["num_state"] == 3:
            coloration.insert(ind, "has-background-grey-lighter")

    return render_template("servers.html", servers=enumerate(servers), coloration=coloration)


@app.route('/table')
def table():
    result = [
        (1000, 16, "К.Г.Б."),  # Score, Servers hijacked, Team Name
        (100, 3, "Угрюмые Моржи"),
        (400, 5, "Как назвать?")
    ]

    result.sort(key=lambda team: team[0])  # Сортируем для вывода в таблице в правильном порядке.
    result.reverse()

    return render_template("table.html", result=enumerate(result))


if __name__ == '__main__':
    app.run()

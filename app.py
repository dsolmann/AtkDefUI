from flask import Flask, render_template

app = Flask(__name__)


@app.route('/')
def index():
    return render_template("index.html")


@app.route('/servers')
def server_state():
    return render_template("servers.html")


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

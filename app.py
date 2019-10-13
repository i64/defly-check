from flask import Flask, jsonify, request

from worker import Worker

app = Flask(__name__)


@app.route("/api/check-team/<string:region>/", methods=["GET"])
def check_team(region):
    return jsonify(Worker.check_server(region))


@app.route("/api/check-teams", methods=["GET"])
def checkTeams():
    return jsonify(Worker.check_servers())


if __name__ == "__main__":
    app.run(host="127.0.0.1", port="5002", debug=True)

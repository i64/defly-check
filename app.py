from flask import Flask, jsonify, request
import os

import worker

if os.getenv("IS_HEROKU"):
    worker.set_interval(worker.re_heroku, 60 * 59)

app = Flask(__name__)


@app.route("/api/check-team/<string:region>/", methods=["GET"], strict_slashes=False)
@app.route("/api/check-team/<string:region>/<int:port>", methods=["GET"], strict_slashes=False)
def check_team(region, port=None):
    return jsonify(worker.check_server(region, port=port))


@app.route("/api/check-teams", methods=["GET"], strict_slashes=False)
def checkTeams():
    return jsonify(worker.check_servers())


if __name__ == "__main__":
    app.run()

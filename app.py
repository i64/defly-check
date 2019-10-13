from flask import Flask, jsonify, request, render_template
from flask_restful import Resource, Api

from worker import Worker


class CheckTeam(Resource):
    def get(self, region):
        return jsonify(Worker.check_server(region))

class CheckTeams(Resource):
    def get(self):
        return jsonify(Worker.check_servers())


app = Flask(__name__)
api = Api(app)

api.add_resource(CheckTeam, '/api/check-team/<region>/')
api.add_resource(CheckTeams, '/api/check-teams')

if __name__ == '__main__':
    app.run(host="127.0.0.1", port='5002', debug=True)
#https://flask-restful.readthedocs.io/en/latest/
#Production mode için: https://flask.palletsprojects.com/en/stable/deploying/
import os
from flask import Flask
from flask_restful import Resource, Api
from sys import path

path.append("")

from config import rest_api

app = Flask(__name__)
api = Api(app)

access = False if open(os.path.join(rest_api.incidents_path)).read() == 0 else True
class Status(Resource):
    def get(self):
        return {
            "error": "endpointcantbeusedalone"
        }

    class English(Resource):
        def get(self):
            incident = None
            try:
                file = open(os.path.join(rest_api.incidents_path, "english.txt"), "r", encoding="utf-8")
                incident = file.read()
            except FileNotFoundError:
                return {
                    "error": "missingindicentfile"
                }
            else:
                return {
                    "access": access,
                    "text": incident
                }
    class Arabic(Resource):
        def get(self):
            incident = None
            try:
                file = open(os.path.join(rest_api.incidents_path, "arabic.txt"), "r", encoding="utf-8")
                incident = file.read()
            except FileNotFoundError:
                return {
                    "error": "missingindicentfile"
                }
            else:
                return {
                    "access": access,
                    "text": incident
                }
    class Japanese(Resource):
        def get(self):
            incident = None
            try:
                file = open(os.path.join(rest_api.incidents_path, "japanese.txt"), "r", encoding="utf-8")
                incident = file.read()
            except FileNotFoundError:
                return {
                    "error": "missingindicentfile"
                }
            else:
                return {
                    "access": access,
                    "text": incident
                }
    class Turkish(Resource):
        def get(self):
            incident = None
            try:
                file = open(os.path.join(rest_api.incidents_path, "turkish.txt"), "r", encoding="utf-8")
                incident = file.read()
            except FileNotFoundError:
                return {
                    "access": access,
                    "error": "missingindicentfile"
                }
            else:
                return {
                    "access": access,
                    "text": incident
                }

api.add_resource(Status, "{}/status".format(rest_api.path), "{}/status/".format(rest_api.path))
api.add_resource(Status.English, "{}/status/english".format(rest_api.path), "{}/status/english/".format(rest_api.path))
api.add_resource(Status.Arabic, "{}/status/arabic".format(rest_api.path), "{}/status/arabic/".format(rest_api.path))
api.add_resource(Status.Japanese, "{}/status/japanese".format(rest_api.path), "{}/status/japanese/".format(rest_api.path))
api.add_resource(Status.Turkish, "{}/status/turkish".format(rest_api.path), "{}/status/turkish/".format(rest_api.path))

app.run(host=rest_api.host, port=rest_api.port)
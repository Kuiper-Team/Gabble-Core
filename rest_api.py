#https://flask-restful.readthedocs.io/en/latest/
import os
from flask import Flask
from flask_restful import Resource, Api
from sys import path

path.append("")

from config import rest_api

app = Flask(__name__)
api = Api(app)

class Status(Resource):
    def get(self):
        return {
            "error": "endpointcantbeusedalone"
        }

    class English(Resource):
        def get(self):
            incident = None
            try:
                file = open(os.path.join("incident", "english.txt"), "r")
                incident = file.read()
            except FileNotFoundError:
                return {
                    "error": "missingindicentfile"
                }
            else:
                return {
                    "text": incident
                }
    class Arabic(Resource):
        def get(self):
            incident = None
            try:
                file = open(os.path.join("incident", "arabic.txt"), "r")
                incident = file.read()
            except FileNotFoundError:
                return {
                    "error": "missingindicentfile"
                }
            else:
                return {
                    "text": incident
                }
    class Japanese(Resource):
        def get(self):
            incident = None
            try:
                file = open(os.path.join("incident", "japanese.txt"), "r")
                incident = file.read()
            except FileNotFoundError:
                return {
                    "error": "missingindicentfile"
                }
            else:
                return {
                    "text": incident
                }
    class Turkish(Resource):
        def get(self):
            incident = None
            try:
                file = open(os.path.join("incident", "turkish.txt"), "r")
                incident = file.read()
            except FileNotFoundError:
                return {
                    "error": "missingindicentfile"
                }
            else:
                return {
                    "text": incident
                }


api.add_resource(Status, "{}/status".format(rest_api.path))
api.add_resource(Status.English, "{}/status/english".format(rest_api.path))
api.add_resource(Status.Arabic, "{}/status/arabic".format(rest_api.path))
api.add_resource(Status.Japanese, "{}/status/japanese".format(rest_api.path))
api.add_resource(Status.Turkish, "{}/status/turkish".format(rest_api.path))

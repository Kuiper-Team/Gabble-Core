#WebRTC ile dosya aktarımı (JavaScript): https://github.com/Mitrajit/Sharenetic
#https://flask-restful.readthedocs.io/en/latest/
import os
from flask import Flask
from flask_restful import Resource, Api
from sys import path

path.append("..")

from config import rest_api

app = Flask(__name__)
api = Api(app)

class Status(Resource):
    def get(self):
        english, arabic, japanese, turkish = (None,) * 4
        try:
            file_1 = open(os.path.join("incident", "english.txt"), "r")
            english = file_1.read()

            file_2 = open(os.path.join("incident", "arabic.txt"), "r")
            arabic = file_2.read()

            file_3 = open(os.path.join("incident", "japanese.txt"), "r")
            japanese = file_3.read()

            file_4 = open(os.path.join("incident", "turkish.txt"), "r")
            turkish = file_4.read()
        except FileNotFoundError:
            return {
                "error": "missingindicentfile"
            }
        else:
            return {
                "english": english,
                "arabic": arabic,
                "japanese": japanese,
                "turkish": turkish
            }
    def post(self):
        return Status.get(self)

api.add_resource(Status, "{}/status".format(rest_api.path))
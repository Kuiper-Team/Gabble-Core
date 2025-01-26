#https://flask-restful.readthedocs.io/en/latest/
#Production mode için: https://flask.palletsprojects.com/en/stable/deploying/
#Not found handling için: https://www.geeksforgeeks.org/python-404-error-handling-in-flask/
import os
import sqlite3
from datetime import datetime
from flask import Flask
from flask_restful import Resource, Api, reqparse
from sys import path

path.append("..")

import database.session_uuids as session_uuids
import database.users as users
import utilities.generation as generation
from config import rest_api
from database.connection import cursor

app = Flask(__name__)
api = Api(app)

parser = reqparse.RequestParser()
parser.add_argument(
    "session_uuid",
    "username",
    "password",
    "expiry"
)

access = False if open(os.path.join(rest_api.incidents_path), "access.txt").read() == 0 else True
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

class CreateSession(Resource):
    def get(self):
        return {
            "error": "usepost"
        }
    def post(self):
        arguments = parser.parse_args()
        username = arguments["username"]
        password = arguments["password"]
        expiry = arguments["expiry"]

        now_ts = generation.unix_timestamp(datetime.now())
        if not(username and password and expiry):
            return {
                "error": "missingarguments"
            }
        elif not users.exists(username):
            return {
                "error": "nouser"
            }
        elif not (now_ts < expiry < now_ts + 31536000): #365 günden fazla süre oturum açık kalamaz.
            return {
                "error": "invalidexpiry"
            }
        check, hash = users.check_credentials(username, password)
        if check:
            session_uuid = None
            try:
                session_uuid = session_uuids.create(username, expiry, hash)
            except Exception as code:
                return {
                    "error": code
                }
            else:
                return {
                    "uuid": session_uuid
                }
        else:
            return {
                "error": "incorrectpassword"
            }

class User(Resource):
    def get(self):
        return {
            "error": "usepost"
        }
    def post(self):
        arguments = parser.parse_args()
        session_uuid = arguments["session_uuid"]
        username = arguments["username"]

        if not (session_uuid and username):
            return {
                "error": "missingarguments"
            }
        data, profile = (None,) * 2
        try:
            data = cursor.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
        except sqlite3.OperationalError:
            return {
                "error": "couldntfetchfromdb"
            }
        else:
            check = session_uuids.check(session_uuid)
            if session_uuid and check[0] and username == check[1]:
                return {
                    "data": {
                        "public": {
                            "username": username,
                            "toc": data[1],
                            "biography": data[7]
                        },
                        "private": {
                            "settings": data[3],
                            "group_settings": data[4]
                        }
                    },
                }
            else:
                return {
                    "data": {
                        "public": {
                            "username": username,
                            "toc": data[1]
                        }
                    }
                }

class CreateUser(Resource):
    def get(self):
        return {
            "error": "usepost"
        }
    def post(self):
        arguments = parser.parse_args()
        username = arguments["username"]
        password = arguments["password"]

        if not (
            3 <= len(username) <= 36 and
            18 <= len(password) <= 45
        ) and ":," in username:
            return {
                "error": "invalidusername"
            }
        try:
            username.decode("ascii")
        except UnicodeDecodeError:
            return {
                "error": "invalidusername"
            }
        try:
            password.decode("ascii")
        except UnicodeDecodeError:
            return {
                "error": "invalidpassword"
            }

        try:
            users.create(arguments["username"], arguments["password"])
        except Exception as code:
            return {
                "error": code
            }
        else:
            return {
                "success": True,
                "user": {
                    "username": arguments["username"],
                    "hash": arguments["password"],
                }
            }

api.add_resource(Status, "{}/status".format(rest_api.path), "{}/status/".format(rest_api.path))
api.add_resource(Status.English, "{}/status/english".format(rest_api.path), "{}/status/english/".format(rest_api.path))
api.add_resource(Status.Arabic, "{}/status/arabic".format(rest_api.path), "{}/status/arabic/".format(rest_api.path))
api.add_resource(Status.Japanese, "{}/status/japanese".format(rest_api.path), "{}/status/japanese/".format(rest_api.path))
api.add_resource(Status.Turkish, "{}/status/turkish".format(rest_api.path), "{}/status/turkish/".format(rest_api.path))

api.add_resource(CreateSession, "{}/signin".format(rest_api.path), "{}/signin/".format(rest_api.path))

api.add_resource(User, "{}/user".format(rest_api.path), "{}/user/".format(rest_api.path))
api.add_resource(CreateUser, "{}/user/create".format(rest_api.path), "{}/user/create/".format(rest_api.path))

app.run(host=rest_api.host, port=rest_api.port)
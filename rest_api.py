#https://flask-restful.readthedocs.io/en/latest/
#Production mode için: https://flask.palletsprojects.com/en/stable/deploying/
#Not found handling için: https://www.geeksforgeeks.org/python-404-error-handling-in-flask/
#HATALAR için HTTP hata kodları eklenecek.
import os
import sqlite3
from datetime import datetime
from flask import Flask
from flask_restful import Resource, Api, reqparse
from sys import path

path.append("..")

import database.requests as requests
import database.session_uuids as session_uuids
import database.users as users
import utilities.generation as generation
from config import rest_api, message
from database.connection import cursor

app = Flask(__name__)
api = Api(app)

parser = reqparse.RequestParser()
parser.add_argument(
    "session_uuid",
    "username",
    "password",
    "expiry",
    "sender",
    "recipient",
    "message"
)

@app.errorhandler(404)
def error_404(error):
    return {
        "success": False,
        "error": "notfound",
    }, 404

usepost = {
    "success": False,
    "error": "usepost"
}
missingarguments = {
    "success": False,
    "error": "missingargument"
}
invalidsessionuuid = {
    "success": False,
    "error": "invalidsessionuuid"
}
nouser = {
    "success": False,
    "error": "nouser"
}
success = {
    "success": True
}
access = False if open(os.path.join(rest_api.incidents_path, "access.txt")).read() == 0 else True
class Status(Resource):
    def get(self):
        return {
            "success": False,
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
                    "success": False,
                    "error": "missingindicentfile"
                }
            else:
                return {
                    "success": True,
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
                    "success": False,
                    "error": "missingindicentfile"
                }
            else:
                return {
                    "success": True,
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
                    "success": False,
                    "error": "missingindicentfile"
                }
            else:
                return {
                    "success": True,
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
                    "success": False,
                    "access": access,
                    "error": "missingindicentfile"
                }
            else:
                return {
                    "success": True,
                    "access": access,
                    "text": incident
                }

class CreateSession(Resource):
    def get(self):
        return usepost
    def post(self):
        arguments = parser.parse_args()
        username = arguments["username"]
        password = arguments["password"]
        expiry = arguments["expiry"]

        now_ts = generation.unix_timestamp(datetime.now())
        if not(username and password and expiry):
            return missingarguments
        elif not users.exists(username):
            return nouser
        elif not (now_ts < expiry < now_ts + 31536000): #365 günden fazla süre oturum açık kalamaz.
            return {
                "success": False,
                "error": "invalidexpiry"
            }
        check, hash = users.check_credentials(username, password)
        if check:
            session_uuid = None
            try:
                session_uuid = session_uuids.create(username, expiry, hash)
            except Exception as code:
                return {
                    "success": False,
                    "error": code
                }
            else:
                return {
                    "success": True,
                    "uuid": session_uuid
                }
        else:
            return {
                "success": False,
                "error": "incorrectpassword"
            }

class User(Resource):
    def get(self):
        return usepost
    def post(self):
        arguments = parser.parse_args()
        username = arguments["username"]
        session_uuid = arguments["session_uuid"]

        if not (session_uuid and username):
            return missingarguments
        data = None
        try:
            data = cursor.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
        except sqlite3.OperationalError:
            return {
                "success": False,
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

class CreateAccount(Resource):
    def get(self):
        return usepost
    def post(self):
        arguments = parser.parse_args()
        username = arguments["username"]
        password = arguments["password"]

        if not (
            3 <= len(username) <= 36 and
            18 <= len(password) <= 45
        ) and ":," in username:
            return {
                "success": False,
                "error": "invalidusername"
            }
        try:
            username.decode("ascii")
        except UnicodeDecodeError:
            return {
                "success": False,
                "error": "invalidusername"
            }
        try:
            password.decode("ascii")
        except UnicodeDecodeError:
            return {
                "success": False,
                "error": "invalidpassword"
            }

        hash = None
        try:
            hash = users.create(arguments["username"], arguments["password"])
        except Exception as code:
            return {
                "success": False,
                "error": code
            }
        else:
            try:
                session_uuids.create(username, generation.unix_timestamp(datetime.now()) + 86400, hash) #İlk oturum açılışında 1 gün süre verilir.
            except Exception as code:
                return {
                    "success": False,
                    "error": code
                }
            else:
                return {
                    "success": True,
                    "user": {
                        "username": username,
                        "hash": generation.hashed_password(password)
                    }
                }

class DeleteAccount(Resource):
    def get(self):
        return usepost
    def post(self):
        arguments = parser.parse_args()
        username = arguments["username"]
        session_uuid = arguments["session_uuid"]

        check = session_uuids.check(session_uuid)
        if not (username and session_uuid):
            return missingarguments
        elif not (check[0] and username == check[1]):
            return invalidsessionuuid
        elif not users.exists(username):
            return nouser
        try:
            users.delete(session_uuid)
        except Exception as code:
            return {
                "success": False,
                "error": code
            }
        else:
            return success

class UpdateAccount(Resource):
    def get(self):
        return usepost
    def post(self):
        arguments = parser.parse_args()
        username = arguments["username"]
        session_uuid = arguments["session_uuid"]

        check = session_uuids.check(session_uuid)
        if not (username and session_uuid):
            return missingarguments
        elif not (users.exists(username)):
            return nouser
        elif not (check[0] and username == check[1]):
            return invalidsessionuuid

        #users modülündeki update ve apply ile başlayanlar arasında seçimLER yaptırılacak ve hepsine uygulanacak.

class SendFriendRequest(Resource):
    def get(self):
        return usepost
    def post(self):
        arguments = parser.parse_args()
        sender = arguments["sender"]
        recipient = arguments["recipient"]
        message = arguments["message"]
        session_uuid = arguments["session_uuid"]

        check = session_uuids.check(session_uuid)
        if not (sender and recipient and session_uuid):
            return missingarguments
        elif not users.exists(sender):
            return {
                "success": False,
                "error": "nosender"
            }
        elif not users.exists(recipient):
            return {
                "success": False,
                "error": "norecipient"
            }
        elif not (check[0] and sender == check[1]):
            return invalidsessionuuid

        hash = None
        try:
            hash = session_uuids.get_hash(session_uuid)
            requests.send(sender, generation.aes_encrypt(recipient, hash), message, 0, generation.unix_timestamp(datetime.now()) + 604800, hash) #7 gün içinde dönüt olmazsa silinir.
        except Exception as code:
            return {
                "success": False,
                "error": code
            }
        else:
            return success

class CancelFriendRequest(Resource):
    def get(self):
        return usepost
    def post(self):
        arguments = parser.parse_args()
        sender = arguments["sender"]
        uuid = arguments["uuid"]
        session_uuid = arguments["session_uuid"]

        check = session_uuids.check(session_uuid)
        if not (uuid and session_uuid):
            return missingarguments
        elif not (check[0] and sender == check[1]):
            return invalidsessionuuid

        try:
            requests.cancel(uuid)
        except Exception as code:
            return {
                "success": False,
                "error": code
            }
        else:
            return success

class AcceptFriendRequest(Resource):
    def get(self):
        return usepost
    def post(self):
        arguments = parser.parse_args()
        username = arguments["username"]
        uuid = arguments["uuid"]
        session_uuid = arguments["session_uuid"]

        check = session_uuids.check(session_uuid)
        if not (uuid and session_uuid):
            return missingarguments
        elif not (check[0] and username == check[1]):
            return invalidsessionuuid

api.add_resource(Status, "{}/status".format(rest_api.path), "{}/status/".format(rest_api.path))
api.add_resource(Status.English, "{}/status/english".format(rest_api.path), "{}/status/english/".format(rest_api.path))
api.add_resource(Status.Arabic, "{}/status/arabic".format(rest_api.path), "{}/status/arabic/".format(rest_api.path))
api.add_resource(Status.Japanese, "{}/status/japanese".format(rest_api.path), "{}/status/japanese/".format(rest_api.path))
api.add_resource(Status.Turkish, "{}/status/turkish".format(rest_api.path), "{}/status/turkish/".format(rest_api.path))

api.add_resource(CreateSession, "{}/signin".format(rest_api.path), "{}/signin/".format(rest_api.path))

api.add_resource(User, "{}/user".format(rest_api.path), "{}/user/".format(rest_api.path))
api.add_resource(CreateAccount, "{}/user/create".format(rest_api.path), "{}/user/create/".format(rest_api.path))
api.add_resource(DeleteAccount, "{}/user/delete".format(rest_api.path), "{}/user/delete/".format(rest_api.path))

app.run(host=rest_api.host, port=rest_api.port)
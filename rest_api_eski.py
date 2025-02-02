#https://flask-restful.readthedocs.io/en/latest/
#Production mode için: https://flask.palletsprojects.com/en/stable/deploying/
#HATALAR için HTTP hata kodları eklenecek.
import os
import sqlite3
from datetime import datetime
from flask import Flask
from flask_restful import Resource, Api, reqparse
from sys import path

path.append("..")

import database.channels as channels
import database.requests as requests
import database.rooms as rooms
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
    "expiry",
    "sender",
    "recipient",
    "message",
    "biography",
    "settings",
    "room_settings",
    "channel_settings",
    "title",
    "type",
    "permission_map"
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
unauthorizedsession = {
    "success": False,
    "error": "unauthorizedsession"
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

        if not (username and session_uuid):
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
            hash = session_uuids.get_hash(session_uuid)
            if check[0] and username == check[1]:
                return {
                    "success": True,
                    "data": {
                        "public": {
                            "username": username,
                            "toc": data[1],
                            "biography": data[7]
                        },
                        "private": {
                            "settings": generation.aes_decrypt(data[3], hash),
                            "group_settings": generation.aes_decrypt(data[4], hash)
                        }
                    },
                }
            else:
                return {
                    "success": True,
                    "data": {
                        "public": {
                            "username": username,
                            "toc": data[1],
                            "biography": data[7]
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
            18 <= len(password) <= 45 and
            all(character not in "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz.;-_!?'\"#%&/\()[]{}=" for character in password)
        ) and ":," in username:
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
        elif not check[0]:
            return invalidsessionuuid
        elif not username == check[1]:
            return unauthorizedsession
        elif not users.exists(username):
            return nouser
        try:
            users.delete(username)
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
        biography = arguments["biography"]
        settings = arguments["settings"]
        room_settings = arguments["room_settings"]
        channel_settings = arguments["channel_settings"]
        session_uuid = arguments["session_uuid"]

        check = session_uuids.check(session_uuid)
        if not (username and session_uuid and biography and settings):
            return missingarguments
        elif not check[0]:
            return invalidsessionuuid
        elif not username == check[1]:
            return unauthorizedsession
        elif not (users.exists(username)):
            return nouser

        try:
            hash = session_uuids.get_hash(session_uuid)
            users.update_biography(generation.aes_encrypt(biography, hash), hash)
            users.apply_settings(username, generation.aes_encrypt(settings, hash), hash)
        except Exception as code:
            return {
                "success": False,
                "error": code
            }
        if room_settings:
            try:
                users.apply_room_settings(username, generation.aes_encrypt(room_settings, hash), hash)
            except Exception as code:
                return {
                    "success": False,
                    "error": code
                }
        if channel_settings:
            try:
                users.apply_channel_settings(username, generation.aes_encrypt(channel_settings, hash), hash)
            except Exception as code:
                return {
                    "success": False,
                    "error": code
                }

        return {
            "success": True
        }

class FriendRequest(Resource):
    def get(self):
        return usepost
    def post(self):
        arguments = parser.parse_args()
        username = arguments["username"]
        uuid = arguments["uuid"]
        session_uuid = arguments["session_uuid"]

        if not (username and uuid and session_uuid):
            return missingarguments
        data = None
        try:
            data = cursor.execute("SELECT * FROM requests WHERE uuid = ?", (username,)).fetchone()
        except sqlite3.OperationalError:
            return {
                "success": False,
                "error": "couldntfetchfromdb"
            }
        else:
            check = session_uuids.check(session_uuid)
            if not (username == data[0] or username == data[1]):
                return {
                    "success": False,
                    "error": "notsenderorrecipient"
                }
            elif not (check[0] and username == check[1]):
                return unauthorizedsession
            else:
                return {
                    "success": True,
                    "data": {
                        "sender": data[0],
                        "recipient": data[1],
                        "uuid": data[2],
                        "type": data[3],
                        "expiry": data[4]
                    }
                }

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
        elif not check[0]:
            return invalidsessionuuid
        elif not sender == check[1]:
            return unauthorizedsession
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
        sender = arguments["username"]
        uuid = arguments["uuid"]
        session_uuid = arguments["session_uuid"]

        check = session_uuids.check(session_uuid)
        if not (uuid and session_uuid):
            return missingarguments
        elif not check[0]:
            return invalidsessionuuid
        elif not sender == check[1]:
            return unauthorizedsession

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

        try:
            cursor.execute("SELECT uuid FROM requests WHERE uuid = ?", (uuid,))
        except sqlite3.OperationalError:
            return {
                "success": False,
                "error": "norequest"
            }
        sender = cursor.execute("SELECT sender FROM requests WHERE uuid = ?", (uuid,)).fetchone()[0]
        recipient = cursor.execute("SELECT recipient FROM requests WHERE uuid = ?", (uuid,)).fetchone()[0]
        check = session_uuids.check(session_uuid)
        if not (uuid and session_uuid):
            return missingarguments
        elif not check[0]:
            return invalidsessionuuid
        elif not username == check[1]:
            return unauthorizedsession
        elif not users.exists(username):
            return nouser
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
        elif not username == recipient:
            return {
                "success": False,
                "error": "notrecipient"
            }

        try:
            hash_1 = users.get_hash(sender)
            hash_2 = session_uuids.get_hash(session_uuid)
            users.add_friends(sender, recipient, hash_1, hash_2)
        except sqlite3.OperationalError:
            return {
                "success": False,
                "error": "nouser"
            }
        else:
            try:
                requests.cancel(uuid)
            except Exception as code:
                return {
                    "success": False,
                    "error": code
                }
            else:
                return success

class DeclineFriendRequest(Resource):
    def get(self):
        return usepost
    def post(self):
        arguments = parser.parse_args()
        username = arguments["username"]
        uuid = arguments["uuid"]
        session_uuid = arguments["session_uuid"]

        try:
            cursor.execute("SELECT uuid FROM requests WHERE uuid = ?", (uuid,))
        except sqlite3.OperationalError:
            return {
                "success": False,
                "error": "norequest"
            }
        sender = cursor.execute("SELECT sender FROM requests WHERE uuid = ?", (uuid,)).fetchone()[0]
        recipient = cursor.execute("SELECT recipient FROM requests WHERE uuid = ?", (uuid,)).fetchone()[0]
        check = session_uuids.check(session_uuid)
        if not (uuid and session_uuid):
            return missingarguments
        elif not check[0]:
            return invalidsessionuuid
        elif not username == check[1]:
            return unauthorizedsession
        elif not users.exists(username):
            return nouser
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
        elif not username == recipient:
            return {
                "success": False,
                "error": "notrecipient"
            }

        try:
            requests.cancel(uuid)
        except Exception as code:
            return {
                "success": False,
                "error": code
            }
class Room(Resource):
    def get(self):
        return usepost
    def post(self):
        arguments = parser.parse_args()
        username = arguments["username"]
        uuid = arguments["uuid"]
        session_uuid = arguments["session_uuid"]

        if not (uuid and username and session_uuid):
            return missingarguments
        data = None
        try:
            data = cursor.execute("SELECT * FROM rooms WHERE uuid = ?", (uuid,)).fetchone()
        except sqlite3.OperationalError:
            return {
                "success": False,
                "error": "couldntfetchfromdb"
            }
        else:
            check = session_uuids.check(session_uuid)
            hash = users.get_hash(rooms.owner(uuid))
            owner = None
            try:
                owner = rooms.owner(uuid)
            except Exception as code:
                return {
                    "success": False,
                    "error": code
                }
            if not (check[0] and username == check[1]):
                return unauthorizedsession
                #KULLANICI ADMİN Mİ DEĞİL Mİ ONA GÖRE İKİ IF BLOĞU OLACAK, ADMİN OLAN SETTINGS VE GROUP_SETTINGS DE GÖRECEK.
            elif not (username in rooms.members(uuid, users.get_hash(owner))):
                return {
                    "success": False,
                    "error": "notmember"
                }
            else:
                if rooms.has_permissions(uuid, username, ("all",), session_uuids.get_hash(session_uuid)):
                    return {
                        "success": True,
                        "data": {
                            "public": {
                                "title": generation.aes_decrypt(data[0], hash),
                                "uuid": data[1],
                                "type": data[2],
                                "owner": data[4],
                                "members": generation.aes_decrypt(data[5], hash),
                                "channels": generation.aes_decrypt(data[3], hash),
                            }
                        }
                    }
                else:
                    return {
                        "success": True,
                        "data": {
                            "public": {
                                "title": generation.aes_decrypt(data[0], hash),
                                "uuid": data[1],
                                "type": data[2],
                                "owner": data[4],
                                "members": generation.aes_decrypt(data[5], hash),
                                "channels": generation.aes_decrypt(data[3], hash),
                            },
                            "private": {
                                "settings": generation.aes_decrypt(data[6], hash),
                                "permissions_map": generation.aes_decrypt(data[7], hash)
                            }
                        }
                    }

class CreateRoom(Resource):
    def get(self):
        return usepost
    def post(self):
        arguments = parser.parse_args()
        username = arguments["username"]
        title = arguments["title"]
        type = arguments["type"]
        session_uuid = arguments["session_uuid"]

        check = session_uuids.check(session_uuid)
        if not (username and title and type and session_uuid):
            return missingarguments
        elif not check[0]:
            return invalidsessionuuid
        elif not username == check[1]:
            return unauthorizedsession
        elif not users.exists(username):
            return nouser

        try:
            hash = session_uuids.get_hash(session_uuid)
            rooms.create(title, type, username, hash)
        except Exception as code:
            return {
                "success": False,
                "error": code
            }
        else:
            return success

class DeleteRoom(Resource):
    def get(self):
        return usepost
    def post(self):
        arguments = parser.parse_args()
        username = arguments["username"]
        uuid = arguments["uuid"]
        session_uuid = arguments["session_uuid"]

        owner = None
        try:
            owner = rooms.owner(uuid)
        except Exception as code:
            return {
                "success": False,
                "error": code
            }
        else:
            check = session_uuids.check(session_uuid)
            if not (uuid and session_uuid):
                return missingarguments
            elif not check[0]:
                return invalidsessionuuid
            elif not username == check[1]:
                return unauthorizedsession
            elif not users.exists(username):
                return nouser
            elif not rooms.has_permissions(uuid, username, ("all",), session_uuids.get_hash(session_uuid)):
                return {
                    "success": False,
                    "error": "nopermission"
                }
            try:
                rooms.delete(uuid)
            except Exception as code:
                return {
                    "success": False,
                    "error": code
                }
            else:
                return success

class UpdateRoom(Resource):
    def get(self):
        return usepost
    def post(self):
        arguments = parser.parse_args()
        username = arguments["username"]
        uuid = arguments["uuid"]
        title = arguments["title"]
        settings = arguments["settings"]
        permissions_map = arguments["permissions_map"]
        session_uuid = arguments["session_uuid"]

        #İPTAL


class JoinRoom(Resource):
    pass #YAPILACAK.

class AddChannel(Resource):
    def get(self):
        return usepost
    def post(self):
        arguments = parser.parse_args()
        username = arguments["username"]
        room_uuid = arguments["uuid"]
        title = arguments["title"]
        type = arguments["type"]
        session_uuid = arguments["session_uuid"]

        check = session_uuids.check(session_uuid)
        if not (username and room_uuid and title and type and session_uuid):
            return missingarguments
        elif not check[0]:
            return invalidsessionuuid
        elif not username == check[1]:
            return unauthorizedsession
        elif not users.exists(username):
            return nouser

        check = session_uuids.check(session_uuid)
        hash = users.get_hash(rooms.owner(room_uuid))
        owner = None
        try:
            owner = rooms.owner(room_uuid)
        except Exception as code:
            return {
                "success": False,
                "error": code
            }
        if not (check[0] and username == check[1]):
            return unauthorizedsession
            # KULLANICI ADMİN Mİ DEĞİL Mİ ONA GÖRE İKİ IF BLOĞU OLACAK, ADMİN OLAN SETTINGS VE GROUP_SETTINGS DE GÖRECEK.
        elif not (username in rooms.members(room_uuid, users.get_hash(owner))):
            return {
                "success": False,
                "error": "notmember"
            }
        else:
            if rooms.has_permissions(room_uuid, username, ("all",), session_uuids.get_hash(session_uuid)):
                try:
                    rooms.create(title, type, username, hash)
                except Exception as code:
                    return {
                        "success": False,
                        "error": code
                    }
                else:
                    return success
            else:
                return {
                    "success": False,
                    "error": "nopermission"
                }

#room: UpdateRoom(), JoinRoom()
#Daha sonra channels'a geçeceğiz.

api.add_resource(Status, "{}/status".format(rest_api.path), "{}/status/".format(rest_api.path))
api.add_resource(Status.English, "{}/status/english".format(rest_api.path), "{}/status/english/".format(rest_api.path))
api.add_resource(Status.Arabic, "{}/status/arabic".format(rest_api.path), "{}/status/arabic/".format(rest_api.path))
api.add_resource(Status.Japanese, "{}/status/japanese".format(rest_api.path), "{}/status/japanese/".format(rest_api.path))
api.add_resource(Status.Turkish, "{}/status/turkish".format(rest_api.path), "{}/status/turkish/".format(rest_api.path))

api.add_resource(CreateSession, "{}/signin".format(rest_api.path), "{}/signin/".format(rest_api.path))

api.add_resource(User, "{}/user".format(rest_api.path), "{}/user/".format(rest_api.path))
api.add_resource(CreateAccount, "{}/user/create".format(rest_api.path), "{}/user/create/".format(rest_api.path))
api.add_resource(DeleteAccount, "{}/user/delete".format(rest_api.path), "{}/user/delete/".format(rest_api.path))
api.add_resource(UpdateAccount, "{}/user/update".format(rest_api.path), "{}/user/update/".format(rest_api.path))

api.add_resource(FriendRequest, "{}/friend_request".format(rest_api.path), "{}/friend_request/".format(rest_api.path))
api.add_resource(SendFriendRequest, "{}/friend_request/send".format(rest_api.path), "{}/friend_request/send/".format(rest_api.path))
api.add_resource(CancelFriendRequest, "{}/friend_request/cancel".format(rest_api.path), "{}/friend_request/cancel/".format(rest_api.path))
api.add_resource(AcceptFriendRequest, "{}/friend_request/accept".format(rest_api.path), "{}/friend_request/accept/".format(rest_api.path))
api.add_resource(DeclineFriendRequest, "{}/friend_request/decline".format(rest_api.path), "{}/friend_request/decline/".format(rest_api.path))

api.add_resource(Room, "{}/room".format(rest_api.path), "{}/room/".format(rest_api.path))
api.add_resource(CreateRoom, "{}/room/create".format(rest_api.path), "{}/room/create/".format(rest_api.path))
api.add_resource(DeleteRoom, "{}/room/delete".format(rest_api.path), "{}/room/delete/".format(rest_api.path))
api.add_resource(UpdateRoom, "{}/room/update".format(rest_api.path), "{}/room/update/".format(rest_api.path))
api.add_resource(JoinRoom, "{}/room/join".format(rest_api.path), "{}/room/join/".format(rest_api.path))
api.add_resource(AddChannel, "{}/room/add_channel".format(rest_api.path), "{}/room/add_channel/".format(rest_api.path))
#(...)

app.run(host=rest_api.host, port=rest_api.port)
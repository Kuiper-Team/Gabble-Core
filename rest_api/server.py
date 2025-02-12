#Production mode için: https://flask.palletsprojects.com/en/stable/deploying/
import sqlite3
from datetime import datetime
from flask import Flask
from flask_restful import Api, Resource, reqparse

import database.session_uuids as session_uuids
import database.users as users
import utilities.generation as generation
import utilities.validation as validation
from config import rest_api
from database.connection import cursor
from presets import *

app = Flask(__name__)
api = Api(app)

parser = reqparse.RequestParser()
parser.add_argument(
    "biography",
    "channel_settings",
    "expiry",
    "message",
    "password",
    "permission_map"
    "recipient",
    "room_settings",
    "sender",
    "session_uuid",
    "settings",
    "title",
    "type",
    "username",
)

import endpoints

map = { #Tüm endpoint isimleri karşılık geldikleri classlara eşleştirilecek.
    "channel": {
        "channel": endpoints.channel.channel.endpoint
    },
    "friend_request": {
        "friend_request": endpoints.friend_request.friend_request.endpoint,
        "accept": endpoints.friend_request.accept.endpoint,
        "cancel": endpoints.friend_request.cancel.endpoint,
        "decline": endpoints.friend_request.decline.endpoint,
        "send": endpoints.friend_request.send.endpoint
    }
}

def endpoint(endpoint):
    arguments = parser.parse_args()
    if not endpoint.config["arguments"] in arguments:
        return missingarguments

    controls = endpoint.config["controls"]
    queries = []

    check_booleans = controls["check_booleans"]
    fetch_from_db = controls["fetch_from_db"]
    is_integer = controls["is_integer"]
    is_session_user_requested = controls["is_session_user_requested"]
    session_valid = controls["session_expired"]
    username_taken = controls["username_taken"]
    user_exists = controls["user_exists"]
    valid_session_expiry = controls["valid_session_expiry"]
    if check_booleans: #Tuple çıktı
        result = []
        for argument in check_booleans:
            result.append(argument is None)
        if check_booleans["query"]: queries.append(result)
        elif not all(result): return notallofthemaretrue
    if fetch_from_db:
        try:
            data = cursor.execute("SELECT * FROM ? WHERE ? = ?", (fetch_from_db["table"], fetch_from_db["row"], arguments[fetch_from_db["where"]])).fetchone()[0]
        except sqlite3.OperationalError:
            result = False
        else:
            result = True
        if fetch_from_db["query"]: queries.append(result)
        elif not result: return nouser
    if is_integer:
        result = validation.integer(arguments[is_integer["argument"]])
        if is_integer["query"]: queries.append(result)
        elif not result: return invalidformat
    if is_session_user_requested:
        result = arguments[is_session_user_requested["username"]] == session_uuids.owner(arguments[is_session_user_requested["uuid"]])
        if session_valid["query"]: queries.append(result)
        elif not result: return nopermission
    if session_valid:
        now = generation.unix_timestamp(datetime.now())
        result = session_uuids.check(arguments[session_valid["uuid"]])
        if session_valid["query"]:
            queries.append(result)
        elif not result:
            return invalidsessionuuid
    if username_taken:
        for user in username_taken["usernames"]:
            result = users.exists(user)
            if username_taken["query"]: queries.append(result)
            elif not result: return nouser
    if user_exists:
        for user in user_exists["users"]:
            result = users.exists(user)
            if user_exists["query"]: queries.append(result)
            elif not result: return nouser
    if valid_session_expiry:
        now = generation.unix_timestamp(datetime.now())
        result = not (now < arguments[valid_session_expiry["expiry"]] <= now + 31536000)
        if session_valid["query"]: queries.append(result)
        elif not result: return invalidexpiry


    return endpoint(Resource, arguments, queries)

@app.errorhandler(404)
def error_404(error):
    return {
        "success": False,
        "error": "notfound",
    }, 404

#API'ye eklemeler burada olacak.

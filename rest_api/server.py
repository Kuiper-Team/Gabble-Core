#https://flask-restful.readthedocs.io/en/latest/
#Production mode için: https://flask.palletsprojects.com/en/stable/deploying/
#HATALAR için HTTP hata kodları eklenecek.
from datetime import datetime
from flask import Flask
from flask_restful import Api, Resource, reqparse

import database.users as users
import utilities.generation as generation
from config import rest_api
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

map = {
    "channel": {
        "channel": None
    }
}

def endpoint(endpoint):
    arguments = parser.parse_args()
    if not endpoint.config["arguments"]["required"]:
        return missingarguments

    controls = endpoint.config["controls"]
    queries = []

    session_expired = controls["session_expired"]
    user_exists = controls["user_exists"]
    valid_session_expiry = controls["valid_session_expiry"]
    if session_expired:
        now = generation.unix_timestamp(datetime.now())
        result = now >= arguments[session_expired["expiry"]]
        if session_expired["query"]: queries.append(result)
        elif not result: return invalidsessionuuid
    elif user_exists:
        for user in user_exists["users"]:
            result = users.exists(user)
            if user_exists["query"]: queries.append(result)
            elif not result: return nouser
    elif valid_session_expiry:
        now = generation.unix_timestamp(datetime.now())
        result = not (now < arguments[valid_session_expiry["expiry"]] <= now + 31536000)
        if session_expired["query"]: queries.append(result)
        elif not result: return invalidexpiry
    #(...)

    return endpoint(Resource, arguments, queries)

@app.errorhandler(404)
def error_404(error):
    return {
        "success": False,
        "error": "notfound",
    }, 404


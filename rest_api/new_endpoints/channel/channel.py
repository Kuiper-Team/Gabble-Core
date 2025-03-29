import sqlite3
from flask import jsonify

import rest_api.controls as controls
import rest_api.presets as presets
from database.connection import cursor
from api import api

@api.route("/channel", methods=["GET", "POST"])
@api.route("/channel/", methods=["GET", "POST"])
def route(parameters):
    private_key = parameters["private_key"]
    username = parameters["username"]
    uuid = parameters["uuid"]

    if controls.check_parameters(parameters, ("username", "uuid", "private_key")):
        if not controls.access_to_channel(username, uuid, private_key): return jsonify(presets.nopermission, status=403)
    else:
        return jsonify(presets.missingarguments, status=406)

    try:
        data = cursor.execute("SELECT * FROM channels WHERE uuid = ?", (parameters["uuid"],)).fetchone()
    except sqlite3.OperationalError:
        return jsonify(presets.nochannel, status=406)
    except Exception as code:
        return jsonify(
            {
                "success": False,
                "error": code
            },
            status=presets.status_codes[code]
        )

    return jsonify(
        {
            "success": True,
            "data": {
                "title": data[0],
                "room_uuid": data[2],
                "type": data[3],
                "tags": data[6]
            }
        },
        status=200,
    )

def reference():
    return jsonify(
        {
            "methods": {
                "GET": True,
                "POST": True
            },
            "description": "Looks up for a channel in database which has given UUID and displays its data.",
            "sample_request": {},
            "sample_response": {}
        },
        status=200
    )
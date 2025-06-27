import sqlite3
from flask import request

import api.controls as controls
import api.presets as presets
from app import api
from database.connection import cursor

@api.route("/channel", methods=["GET", "POST"])
@api.route("/channel/", methods=["GET", "POST"])
def channel():
    parameters = request.args if request.method == "GET" else request.form

    if controls.check_parameters(parameters, ("username", "uuid", "private_key")):
        username = parameters["username"]
        uuid = parameters["uuid"]
        private_key = parameters["private_key"]

        if not controls.access_to_channel(username, uuid, private_key): return presets.nopermission
    else:
        return presets.missingparameter

    try:
        data = cursor.execute("SELECT * FROM channels WHERE uuid = ?", (parameters["uuid"],)).fetchone()
    except sqlite3.OperationalError:
        return presets.nochannel
    except Exception as code:
        return {
                "success": False,
                "error": code
            }, presets.status_codes[code]

    return {
            "success": True,
            "data": {
                "title": data[0],
                "room_uuid": data[2],
                "type": data[3],
                "tags": data[6]
            }
        }, 200
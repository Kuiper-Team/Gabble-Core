from flask import request

import api.controls as controls
import api.presets as presets
import database.rooms as rooms
import utilities.generation as generation
from api.app import api
from api.presets import missingparameter


@api.route("/room", methods=["GET", "POST"])
@api.route("/room/", methods=["GET", "POST"])
def room():
    parameters = request.args if request.method == "GET" else request.form

    if controls.check_parameters(parameters, ("uuid", "username", "private_key")):
        uuid = parameters["uuid"]
        username = parameters["username"]
        private_key = parameters["private_key"]

        if not controls.access_to_room(username, uuid, private_key): return presets.nopermission

        administrator_hash = None
        if controls.check_parameters(parameters, ("administrator_hash",)):
            administrator_hash = parameters["administrator_hash"]

            if not controls.access_to_sensitive_data(uuid, administrator_hash): return presets.nopermission
    else:
        return missingparameter

    try:
        data = controls.fetch_from_db(parameters, "rooms", "uuid", uuid)
    except Exception as code:
        return {
            "success": False,
            "error": code
        }, presets.status_codes[code]

    if administrator_hash:
        return {
            "success": True,
            "data": {
                "uuid": uuid,
                "title": data[0],
                "public_key": data[2],
                "channels": rooms.channels(uuid, private_key),
                "members": rooms.members(uuid, private_key),
                "sensitive": {
                    "settings": generation.aes_decrypt(data[5], administrator_hash),
                    "permissions": generation.aes_decrypt(data[6], administrator_hash)
                }
            },
        }, 200
    else:
        return {
            "success": True,
            "data": {
                "uuid": uuid,
                "title": data[0],
                "public_key": data[2],
                "channels": rooms.channels(uuid, private_key),
                "members": rooms.members(uuid, private_key),
            }
        }, 200
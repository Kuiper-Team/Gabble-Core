from flask import request

import api.controls as controls
import api.presets as presets
import database.rooms as rooms
import utilities.generation as generation
from api.app import api

@api.route("/room", methods=["GET", "POST"])
@api.route("/room/", methods=["GET", "POST"])
def room():
    parameters = request.args if request.method == "GET" else request.form

    if controls.check_parameters(parameters, ("uuid", "username", "hash", "private_key")):
        uuid = parameters["uuid"]
        username = parameters["username"]
        private_key = parameters["private_key"]

        if not controls.verify_hash(username, parameters["hash"]): return presets.incorrecthash
        if not controls.access_to_room(username, uuid, private_key): return presets.nopermission
    else:
        return presets.missingparameter

    access = rooms.has_permissions(uuid, username, ("access_to_settings", "access_to_permissions"), private_key)
    try:
        data = controls.fetch_from_db("rooms", "uuid", uuid)
    except Exception as code:
        return {
            "success": False,
            "error": code
        }, presets.status_codes[code]

    if access[0] and access[1]:
        return {
            "success": True,
            "data": {
                "uuid": uuid,
                "title": data[0],
                "public_key": data[2],
                "channels": rooms.channels(uuid, private_key),
                "members": rooms.members(uuid, private_key),
                "sensitive": {
                    "settings": generation.rsa_decrypt(data[5], private_key),
                    "permissions": generation.rsa_decrypt(data[6], private_key)
                }
            },
        }, 200
    elif access[0]:
        return {
            "success": True,
            "data": {
                "uuid": uuid,
                "title": data[0],
                "public_key": data[2],
                "channels": rooms.channels(uuid, private_key),
                "members": rooms.members(uuid, private_key),
                "sensitive": {
                    "settings": generation.rsa_decrypt(data[5], private_key)
                }
            },
        }, 200
    elif access[1]:
        return {
            "success": True,
            "data": {
                "uuid": uuid,
                "title": data[0],
                "public_key": data[2],
                "channels": rooms.channels(uuid, private_key),
                "members": rooms.members(uuid, private_key),
                "sensitive": {
                    "permissions": generation.rsa_decrypt(data[6], private_key)
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
                "members": rooms.members(uuid, private_key)
            }
        }, 200
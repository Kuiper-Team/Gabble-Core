from flask import request

import api.controls as controls
import api.presets as presets
import database.rooms as rooms
from api.app import api

@api.route("/room/delete", methods=["GET", "POST"])
@api.route("/room/delete/", methods=["GET", "POST"])
def room_delete():
    parameters = request.args if request.method == "GET" else request.form

    if controls.check_parameters(parameters, ("uuid", "username", "private_key", "administrator_hash")):
        uuid = parameters["uuid"]
        username = parameters["username"]
        private_key = parameters["private_key"]

        if not controls.access_to_room(username, uuid, private_key) or not controls.has_permissions(username, uuid, ("delete_room",), parameters["administrator_hash"]): return presets.nopermission
        if not controls.verify_private_key(username, private_key): return presets.incorrectprivatekey
    else:
        return presets.missingparameter

    try:
        rooms.delete(uuid)
    except Exception as code:
        return {
            "success": False,
            "error": code
        }, presets.status_codes[code]
    else:
        return presets.success, 200
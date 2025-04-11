from flask import request

import api.controls as controls
import api.presets as presets
import database.rooms as rooms
from api.app import api

@api.route("/room/member", methods=["GET", "POST"])
@api.route("/room/member/", methods=["GET", "POST"])
def room_member():
    parameters = request.args if request.method == "GET" else request.form

    if controls.check_parameters(parameters, ("uuid", "member", "username", "hash", "private_key")):
        uuid = parameters["uuid"]
        username = parameters["username"]
        private_key = parameters["private_key"]

        if not controls.verify_hash(username, parameters["hash"]): return presets.incorrecthash
        if not controls.access_to_room(username, uuid, private_key) or not rooms.has_permissions(uuid, username, ("kick_members",), private_key): return presets.nopermission
    else:
        return presets.missingparameter

    try:
        rooms.kick_member(parameters["member"], uuid, private_key)
    except Exception as code:
        return {
            "success": False,
            "error": code
        }, presets.status_codes[code]
    else:
        return presets.success, 200
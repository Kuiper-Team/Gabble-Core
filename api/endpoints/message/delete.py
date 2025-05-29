from flask import request

import api.controls as controls
import api.presets as presets
import database.messages as messages
from app import api

@api.route("/message/delete", methods=["GET", "POST"])
@api.route("/message/delete/", methods=["GET", "POST"])
def message_delete():
    parameters = request.args if request.method == "GET" else request.form

    if controls.check_parameters(parameters, ("uuid", "channel_uuid", "private_key", "username", "hash")):
        channel_uuid = parameters["channel_uuid"]
        username = parameters["username"]
        private_key = parameters["private_key"]

        if not controls.access_to_channel(username, channel_uuid, private_key): return presets.nopermission
        if not controls.verify_hash(username, parameters["hash"]): return presets.incorrecthash
    else:
        return presets.missingparameter

    try:
        messages.delete(parameters["uuid"], channel_uuid)
    except Exception as code:
        return {
            "success": False,
            "error": code
        }, presets.status_codes[code]
    else:
        return presets.success, 200
from flask import request

import api.controls as controls
import api.presets as presets
import database.channels as channels
import database.messages as messages
import utilities.generation as generation
from app import api

@api.route("/message/create", methods=["GET", "POST"])
@api.route("/message/create/", methods=["GET", "POST"])
def message_create():
    parameters = request.args if request.method == "GET" else request.form

    if controls.check_parameters(parameters, ("message", "channel_uuid", "username", "hash", "public_key", "private_key")):
        username = parameters["username"]
        private_key = parameters["private_key"]
        channel_uuid = parameters["channel_uuid"]

        if not controls.access_to_channel(username, channel_uuid, private_key): return presets.nopermission
        if not controls.verify_hash(username, parameters["hash"]): return presets.incorrecthash
    else:
        return presets.missingparameter

    try:
        message = generation.aes_decrypt(parameters["message"], private_key)
    except Exception:
        return presets.invalidformat
    length = len(message)
    if 1 > length > 1000: return presets.invalidformat

    try:
        data = messages.create(message, username, channel_uuid, parameters["public_key"])
    except Exception as code:
        return {
            "success": False,
            "error": code
        }, presets.status_codes[code]
    else:
        return {
            "success": True,
            "message": {
                "message": message,
                "uuid": data[0],
                "room_uuid": channels.room_of(channel_uuid),
                "channel_uuid": channel_uuid,
                "timestamp": data[1]
            }
        }, 201
from flask import request

import api.controls as controls
import api.presets as presets
import utilities.generation as generation
from app import api

@api.route("/message", methods=["GET", "POST"])
@api.route("/message/", methods=["GET", "POST"])
def message():
    parameters = request.args if request.method == "GET" else request.form

    if controls.check_parameters(parameters, ("uuid", "username", "hash")):
        uuid = parameters["uuid"]
        username = parameters["username"]
        private_key = parameters["private_key"]

        if not controls.verify_hash(username, parameters["hash"]): return presets.incorrecthash
        if not controls.access_to_channel(username, uuid, private_key): return presets.nopermission
    else:
        return presets.missingparameter

    try:
        data = controls.fetch_from_db("message", "uuid", uuid)
    except Exception as code:
        return {
            "success": False,
            "error": code
        }, presets.status_codes[code]

    return {
        "success": True,
        "data": {
            "uuid": uuid,
            "room_uuid": data[2],
            "channel_uuid": data[3],
            "timestamp": generation.rsa_decrypt(data[4], private_key),
            "body": generation.rsa_decrypt(data[0], private_key)
        },
    }, 200
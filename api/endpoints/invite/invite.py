from flask import request

import api.controls as controls
import api.presets as presets
import utilities.generation as generation
from app import api

@api.route("/invite", methods=["GET", "POST"])
@api.route("/invite/", methods=["GET", "POST"])
def invite():
    parameters = request.args if request.method == "GET" else request.form

    if controls.check_parameters(parameters, ("uuid", "passcode", "username", "hash")):
        uuid = parameters["uuid"]
        passcode = parameters["passcode"]
        username = parameters["username"]

        if not controls.verify_hash(username, parameters["hash"]): return presets.incorrecthash
        if not controls.verify_passcode(uuid, passcode): return presets.incorrectpasscode
    else:
        return presets.missingparameter

    try:
        data = controls.fetch_from_db("invite", "uuid", uuid)
    except Exception as code:
        return {
            "success": False,
            "error": code
        }, presets.status_codes[code]

    result = generation.aes_decrypt(data[3], passcode).split(",")
    if result[0] == "f":
        return {
            "success": True,
            "data": {
                "uuid": uuid,
                "type": result[0],
                "inviter": data[1],
                "invitee": result[2],
                "expiry": data[2]
            },
        }, 200
    elif result[1] == "r":
        return {
            "success": True,
            "data": {
                "uuid": uuid,
                "type": result[0],
                "inviter": data[1],
                "invitee": result[2],
                "room_uuid": result[1],
                "expiry": data[2]
            }
        }, 200
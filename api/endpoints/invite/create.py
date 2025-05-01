#Don't forget to append the notice to the target user's inbox.
from datetime import datetime
from flask import request

import api.controls as controls
import api.presets as presets
import database.invites as invites
import utilities.generation as generation
import utilities.validation as validation
from api.app import api

@api.route("/invite/create", methods=["GET", "POST"])
@api.route("/invite/create/", methods=["GET", "POST"])
def invite_create():
    parameters = request.args if request.method == "GET" else request.form

    if controls.check_parameters(parameters, ("type", "expiry", "passcode", "username", "hash")):
        type = parameters["type"]
        expiry = parameters["expiry"]
        passcode = parameters["passcode"]
        username = parameters["username"]

        f = type == "f"
        i = type == "i"
        if f:
            if not controls.check_parameters(parameters, ("target")): return presets.missingparameter
        elif i:
            if not controls.check_parameters(parameters, ("room_uuid")): return presets.missingparameter
        else:
            return presets.invalidformat

        now = generation.unix_timestamp(datetime.now())
        if not (
            validation.timestamp(expiry) and
             now + 60 <= expiry <= now + 31556926
        ): return presets.invalidexpiry

        if not controls.verify_hash(username, parameters["hash"]): return presets.incorrecthash
    else:
        return presets.missingparameter

    try:
        if f:
            invites.create(username, expiry, "f,{},{}".format(username, parameters["target"]), passcode)
        elif i:
            invites.create(username, expiry, "i,{},{}".format(parameters["room_uuid"], username), passcode)
    except Exception as code:
        return {
            "success": False,
            "error": code
        }, presets.status_codes[code]
from flask import request

import api.controls as controls
import api.presets as presets
import database.invites as invites
import database.users as users
import utilities.validation as validation
from api.app import api


@api.route("/invite/accept", methods=["GET", "POST"])
@api.route("/invite/accept/", methods=["GET", "POST"])
def invite_accept():
    parameters = request.args if request.method == "GET" else request.form

    if controls.check_parameters(parameters, ("uuid", "passcode", "username", "hash")):
        uuid = parameters["uuid"]
        passcode = parameters["passcode"]
        username = parameters["username"]
        hash = parameters["hash"]

        result = controls.fetch_invite_result(uuid, passcode)

        if not controls.verify_hash(username, parameters["hash"]): return presets.incorrecthash
        if not controls.verify_passcode(uuid, passcode): return presets.incorrectpasscode
        if not validation.timestamp(controls.fetch_from_db("invites", "uuid", uuid, column="expiry")): return presets.inviteexpired

        if result[0] == "f":
            if not result[1] == username: return presets.nopermission
            if not result[2] in users.friends(username, hash): return presets.alreadyfriends
        elif result[0] == "r":
            if result[1] in users.key_chain(username, hash): return presets.alreadyamember
    else:
        return presets.missingparameter

    try:
        invites.accept(uuid, passcode, room_private_key=parameters["private_key"])
    except Exception as code:
        return {
            "success": False,
            "error": code
        }, presets.status_codes[code]
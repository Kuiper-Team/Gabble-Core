from flask import request

import api.controls as controls
import api.presets as presets
import database.rooms as rooms
import utilities.generation as generation
from app import api

@api.route("/room/update", methods=["GET", "POST"])
@api.route("/room/update/", methods=["GET", "POST"])
def room_update():
    parameters = request.args if request.method == "GET" else request.form

    if controls.check_parameters(parameters, ("uuid", "username", "private_key")):
        uuid = parameters["uuid"]
        username = parameters["username"]
        private_key = parameters["private_key"]

        if not controls.verify_hash(parameters["username"], parameters["hash"]): return presets.incorrecthash
        if not rooms.has_permissions(username, uuid, ("update_settings"), private_key): return presets.nopermission
    else:
        return presets.missingparameter

    changes = 0
    settings, permissions = (None,) * 2
    if controls.check_parameters(parameters, ("settings",)):
        settings = parameters["settings"]
        changes += 1
    if controls.check_parameters(parameters, ("permissions",)):
        permissions = parameters["permissions"]
        changes += 1
    if changes == 0: return presets.missingparameter

    try:
        if settings: settings = generation.rsa_decrypt(settings, private_key)
        if permissions: permissions = generation.rsa_decrypt(permissions, private_key)
        rooms.update(username, settings=settings, permissions=permissions)
    except Exception as code:
        return {
            "success": False,
            "error": code
        }, presets.status_codes[code]

    return presets.success, 201
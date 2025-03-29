from flask import request

import api.controls as controls
import api.presets as presets
import database.users as users
import utilities.generation as generation
from api.app import api

@api.route("/user/update", methods=["GET", "POST"])
@api.route("/user/update/", methods=["GET", "POST"])
def user_update():
    parameters = request.args if request.method == "GET" else request.form

    if controls.check_parameters(parameters, ("username", "hash")):
        username = parameters["username"]
        hash = parameters["hash"]

        if not controls.verify_hash(parameters, username, hash): return presets.incorrecthash
    else:
        return presets.missingparameter

    channel_settings, settings, room_settings = (None,) * 3
    if controls.check_parameters(parameters, ("channel_settings",)): channel_settings = parameters["channel_settings"]
    if controls.check_parameters(parameters, ("settings",)): settings = parameters["settings"]
    if controls.check_parameters(parameters, ("room_settings",)): room_settings = parameters["room_settings"]

    try:
        if settings: settings = generation.aes_encrypt(settings, hash)
        if room_settings: room_settings = generation.aes_encrypt(room_settings, hash)
        if channel_settings: channel_settings = generation.aes_encrypt(channel_settings, hash)
        users.update(username, display_name=parameters["display_name"], settings=settings, room_settings=room_settings, channel_settings=channel_settings, biography=parameters["biography"])
    except Exception as code:
        return {
                "success": False,
                "error": code
            }, presets.status_codes[code]

    return presets.success, 201

def reference():
    pass #(...)
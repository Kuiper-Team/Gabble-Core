from flask import jsonify

import database.users as users
import rest_api.controls as controls
import rest_api.presets as presets
import utilities.generation as generation
from api import api

@api.route("/user/update", methods=["GET", "POST"])
@api.route("/user/update/", methods=["GET", "POST"])
def route(parameters):
    channel_settings = parameters["channel_settings"]
    hash = parameters["hash"]
    room_settings = parameters["room_settings"]
    settings = parameters["settings"]
    username = parameters["username"]

    if controls.check_parameters(parameters, ("username", "hash")):
        if not controls.verify_hash(parameters, username, hash): return jsonify(presets.incorrecthash, status=401)
    else:
        return jsonify(presets.missingarguments, 406)

    try:
        if settings: settings = generation.aes_encrypt(settings, hash)
        if room_settings: room_settings = generation.aes_encrypt(room_settings, hash)
        if channel_settings: channel_settings = generation.aes_encrypt(channel_settings, hash)
        users.update(username, display_name=parameters["display_name"], settings=settings, room_settings=room_settings, channel_settings=channel_settings, biography=parameters["biography"])
    except Exception as code:
        return jsonify(
            {
                "success": False,
                "error": code
            },
            status=presets.status_codes[code]
        )

    return jsonify(presets.success, status=201)

def reference():
    return jsonify(
        {
            "methods": {
                "GET": True,
                "POST": True
            },
            "description": "Updates desired database rows of a user with provided data.",
            "sample_request": {},
            "sample_response": {}
        },
        status=200
    )
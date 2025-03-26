import json

from flask import jsonify

import rest_api.controls as controls
import rest_api.presets as presets
import utilities.generation as generation
from api import api

@api.route("/user", methods=["GET", "POST"])
@api.route("/user/", methods=["GET", "POST"])
def route(parameters):
    hash = parameters["hash"]
    username = parameters["username"]

    data = controls.fetch_from_db(parameters, "users", "username", "username")

    if controls.check_parameters(parameters, ["username", "hash"]):
        if not controls.user_exists(username): return jsonify(presets.nouser, status=406)
        access = controls.verify_hash(parameters, username, hash)
    else:
        return jsonify(presets.missingarguments, status=406)

    if access:
        return {
            "success": True,
            "data": {
                "public": {
                    "username": username,
                    "display_name": data[1],
                    "biography": data[6],
                    "request_hash": data[7]
                },
                "private": {
                    "settings": generation.aes_decrypt(data[2], hash),
                    "room_settings": generation.aes_decrypt(data[3], hash),
                    "channel_settings": generation.aes_decrypt(data[4], hash),
                    "key_chain": json.dumps(generation.aes_decrypt(data[9], hash))
                }
            },
        }
    else:
        return {
            "success": True,
            "data": {
                "public": {
                    "username": username,
                    "display_name": data[1],
                    "biography": data[6],
                    "request_hash": data[7]
                }
            },
        }

def reference():
    return jsonify(
        {
            "methods": {
                "GET": True,
                "POST": True
            },
            "description": "Looks up for a user in the database and displays its public, and if authorized, private data.",
            "sample_request": {},
            "sample_response": {}
        },
        status=200
    )
import json
from flask import request

import api.controls as controls
import api.presets as presets
import utilities.generation as generation
from api.app import api

@api.route("/user", methods=["GET", "POST"])
@api.route("/user/", methods=["GET", "POST"])
def user():
    parameters = request.args if request.method == "GET" else request.form

    data = controls.fetch_from_db(parameters, "users", "username", "username")

    if controls.check_parameters(parameters, ("username", "hash")):
        hash = parameters["hash"]
        username = parameters["username"]

        if not controls.user_exists(username): return presets.nouser
        access = controls.verify_hash(parameters, username, hash)
    else:
        return presets.missingparameter

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
    pass #(...)
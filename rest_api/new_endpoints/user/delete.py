from flask import jsonify

import database.users as users
import rest_api.controls as controls
import rest_api.presets as presets
from api import api

@api.route("/user/delete", methods=["GET", "POST"])
@api.route("/user/delete/", methods=["GET", "POST"])
def route(parameters):
    username = parameters["username"]

    if controls.check_parameters(parameters, ("username", "hash")):
        if not controls.user_exists(username): return jsonify(presets.nouser, status=406)
        if not controls.verify_hash(parameters, username, hash): return jsonify(presets.incorrecthash, status=401)
    else:
        return jsonify(presets.missingarguments, status=406)

    try:
        users.delete(username, parameters["hash"])
    except Exception as code:
        return jsonify(
            {
                "success": False,
                "error": code
            },
            status=presets.status_codes[code]
        )

def reference():
    return jsonify(
        {
            "methods": {
                "GET": True,
                "POST": True
            },
            "description": "Deletes a user account that has given username.",
            "sample_request": {},
            "sample_response": {}
        },
        status=200
    )
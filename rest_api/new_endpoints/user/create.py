from flask import jsonify

import rest_api.controls as controls
import rest_api.presets as presets
import database.users as users
from api import api

@api.route("/user/create", methods=["GET", "POST"])
@api.route("/user/create/", methods=["GET", "POST"])
def route(parameters):
    username = parameters["username"]
    password = parameters["password"]

    if controls.check_parameters(parameters, ("username", "password")):
        if controls.user_exists(username): return jsonify(presets.userexists, status=401)
    else:
        return jsonify(presets.missingarguments, status=406)

    if not (
        3 <= len(username) <= 36 and
        18 <= len(password) <= 45 and
        all(character not in "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz.;-_!?'\"#%&/\()[]{}=" for character in password)
    ): return jsonify(presets.invalidusername, status=406)

    try:
        password.decode("ascii")
    except UnicodeDecodeError:
        return jsonify(presets.incorrectpassword, status=401)

    try:
        hash, salt = users.create(username, password)
    except Exception as code:
        return jsonify(
            {
                "success": False,
                "error": code
            },
            status=presets.status_codes[code]
        )

    return jsonify(
        {
            "success": True,
            "user": {
                "username": username,
                "hash": hash,
                "salt": salt
            }
        },
        status=201
    )

def reference():
    return jsonify(
        {
            "methods": {
                "GET": True,
                "POST": True
            },
            "description": "Registers a new user to the database using provided information.",
            "sample_request": {},
            "sample_response": {}
        },
        status=200
    )
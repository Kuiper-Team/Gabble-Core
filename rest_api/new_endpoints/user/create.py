from flask import jsonify

import rest_api.controls as controls
import database.users as users
from api import api
from rest_api.presets import alreadyamember, incorrectpassword, invalidusername, missingarguments, status_codes

@api.route("/user/create", methods=["GET", "POST"])
@api.route("/user/create/", methods=["GET", "POST"])
def route(parameters):
    username = parameters["username"]
    password = parameters["password"]

    if not controls.check_parameters(parameters, ["username", "password"]): return missingarguments

    if controls.user_exists(parameters["username"]):
        return jsonify(
            alreadyamember,
            status=401
        )

    if not (
        3 <= len(username) <= 36 and
        18 <= len(password) <= 45 and
        all(character not in "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz.;-_!?'\"#%&/\()[]{}=" for character in password)
    ): return jsonify(invalidusername, status=406)

    try:
        password.decode("ascii")
    except UnicodeDecodeError:
        return jsonify(incorrectpassword, status=401)

    try:
        hash, salt = users.create(username, password)
    except Exception as code:
        return jsonify(
            {
                "success": False,
                "error": code
            },
            status=status_codes[code]
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
            "description": "",
            "sample_request": {},
            "sample_response": {}
        },
        status=200
    )
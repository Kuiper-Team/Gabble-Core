from flask import request

import api.controls as controls
import api.presets as presets
import database.rooms as rooms
from app import api

@api.route("/room/create", methods=["GET", "POST"])
@api.route("/room/create/", methods=["GET", "POST"])
def room_create():
    parameters = request.args if request.method == "GET" else request.form

    if controls.check_parameters(parameters, ("title", "username", "hash")):
        title = parameters["title"]
        username = parameters["username"]

        if not controls.verify_hash(username, parameters["hash"]): return presets.incorrecthash
        if controls.fetch_from_db("rooms", "username", username): return presets.roomexists
    else:
        return presets.missingparameter

    if not (
        1 <= len(title) <= 36 and
        title.isascii() and
        all(character in "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz.;-_!?'\"#%&/\\()[]{}=" for character in password)
    ): return presets.invalidformat

    try:
        public_key, private_key, uuid = rooms.create(title, username)
    except Exception as code:
        return {
            "success": False,
            "error": code
        }, presets.status_codes[code]
    else:
        return {
            "success": True,
            "room": {
                "uuid": uuid,
                "title": title,
                "public_key": public_key,
                "private_key": private_key,
            }
        }, 201
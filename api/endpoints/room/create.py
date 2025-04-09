from flask import request

import api.controls as controls
import api.presets as presets
import database.rooms as rooms
from api.app import api

@api.route("/room/create", methods=["GET", "POST"])
@api.route("/room/create/", methods=["GET", "POST"])
def room_create():
    parameters = request.args if request.method == "GET" else request.form

    if controls.check_parameters(parameters, ("title", "username", "hash")):
        title = parameters["title"]
        username = parameters["username"]
        hash = parameters["hash"]

        if not controls.verify_hash(parameters, username, hash): return presets.incorrecthash
        if controls.fetch_from_db(parameters, "rooms", "username", "username"): return presets.roomexists
    else:
        return presets.missingparameter

    if not (
        1 <= len(title) <= 36 and
        title.isascii() and
        all(character not in "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz.;-_!?'\"#%&/\()[]{}=" for character in title)
    ): return presets.invalidformat

    try:
        public_key, private_key, administrator_hash, uuid = rooms.create(title, username)
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
                "administrator_hash": administrator_hash
            }
        }, 201
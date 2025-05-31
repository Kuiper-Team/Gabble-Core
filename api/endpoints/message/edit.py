import sqlite3
from flask import request

import api.controls as controls
import api.presets as presets
import database.messages as messages
import utilities.generation as generation
from app import api
from database.connection import cursor

@api.route("/message/edit", methods=["GET", "POST"])
@api.route("/message/edit/", methods=["GET", "POST"])
def message_edit():
    parameters = request.args if request.method == "GET" else request.form

    if not controls.check_parameters(parameters, ("message", "channel_uuid", "username", "hash", "public_key", "private_key")):
        channel_uuid = parameters["channel_uuid"]
        ciphertext = parameters["message"]
        private_key = parameters["private_key"]
        username = parameters["username"]
        uuid = parameters["uuid"]

        if not controls.access_to_channel(username, channel_uuid, private_key): return presets.nopermission
        if not controls.verify_hash(username, parameters["hash"]): return presets.incorrecthash
    else:
        return presets.missingparameter

    try:
        new_message = generation.aes_decrypt(ciphertext, private_key)
    except Exception:
        return presets.invalidformat
    length = len(new_message)
    if 1 > length > 1000: return presets.invalidformat

    try:
        if ciphertext == cursor.execute("SELECT message FROM messages WHERE uuid = ? AND room_uuid = ? AND channel_uuid = ?", ()).fetchone()[0]: return presets.sameasprevious
    except sqlite3.OperationalError:
        return presets.sameasprevious

    try:
        messages.edit(new_message, uuid, channel_uuid, private_key)
    except Exception as code:
        return {
            "success": False,
            "error": code
        }, presets.status_codes[code]
    else:
        return presets.success, 201
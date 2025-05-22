from flask import request

import api.controls as controls
import api.presets as presets
import database.users as users
from app import api

@api.route("/user/delete", methods=["GET", "POST"])
@api.route("/user/delete/", methods=["GET", "POST"])
def user_delete():
    parameters = request.args if request.method == "GET" else request.form

    if controls.check_parameters(parameters, ("username", "hash")):
        username = parameters["username"]

        if not controls.user_exists(username): return presets.nouser
        if not controls.verify_hash(username, parameters["hash"]): return presets.incorrecthash
    else:
        return presets.missingparameter

    try:
        users.delete(username, parameters["hash"])
    except Exception as code:
        return {
                "success": False,
                "error": code
            }, presets.status_codes[code]
    else:
        return presets.success, 200
from flask import request

import api.controls as controls
import api.presets as presets
import database.messages as messages
from api.app import api

@api.route("/message", methods=["GET", "POST"])
@api.route("/message/", methods=["GET", "POST"])
def message():
    parameters = request.args if request.method == "GET" else request.form


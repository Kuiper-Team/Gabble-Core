from flask import jsonify

from api import api

@api.route("/", methods=["GET", "POST"])
def route(parameters):
    return jsonify(
        {
            "success": True,
            "reference_path": "/reference"
        },
        status=200
    )

def reference():
    return jsonify(
        {
            "methods": {
                "GET": True,
                "POST": True
            },
            "description": "Responds with a path to the API reference.",
            "sample_request": {},
            "sample_response": {} #(...)
        },
        status=200
    )
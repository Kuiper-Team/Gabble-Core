from flask import jsonify

def home(arguments):
    return jsonify(
        [{
            "success": True,
            "reference_path": "/reference"
        }],
        status=200,
        mimetype="application/json"
    )
#I might implement CORS, rate limit and JWT too.
#I can use Kafka instead of the database based inbox system.
#I must add a concise permission system.
#For CORS, see http://medium.com/@mterrano1/cors-in-a-flask-api-38051388f8cc
#The REST API must have a SQL injection attack prevention system.
import utilities.log as log
from flask import Flask, json
from utilities.importer import import_directory

api = Flask(__name__)
json.provider.DefaultJSONProvider.sort_keys = False

try:
    imported = import_directory("api.endpoints", excluded_directory_names=("__pycache",), return_imported_scripts=True)
except Exception:
    log.failure("Could not import all of the endpoints. Make sure that the directory structure and script names are proper.")
else:
    for script in imported:
        log.success("Successfully imported {}.".format(script))


@api.errorhandler(400)
def error_400(error):
    return {
        "success": False,
        "error": "badrequest"
    }, 400

@api.errorhandler(404)
def error_404(error):
    return {
        "success": False,
        "error": "notfound"
    }, 404

@api.errorhandler(405)
def error_405(error):
    return {
        "success": False,
        "error": "methodnotallowed"
    }, 405

@api.errorhandler(415)
def error_416(error):
    return {
        "success": False,
        "error": "unsupportedmediatype"
    }, 415

@api.errorhandler(500)
def error_500(error):
    return {
        "success": False,
        "error": "internalservererror"
    }, 500
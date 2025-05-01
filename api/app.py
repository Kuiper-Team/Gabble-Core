#I might implement CORS, rate limit and JWT too.
#And I can also switch the whole core to more professional frameworks and database management systems.
#For CORS, see http://medium.com/@mterrano1/cors-in-a-flask-api-38051388f8cc
#The REST API must have a SQL injection attack prevention system.
import sys
from flask import Flask, json
from os import environ

api = Flask(__name__)
json.provider.DefaultJSONProvider.sort_keys = False

from endpoints import home
from endpoints.channel import channel, create
from endpoints.conversation import conversation, create, delete
from endpoints.message import message, create, delete, edit
from endpoints.invite import invite, accept, decline, withdraw
from endpoints.room import room, create, delete, update
from endpoints.user import user, create, delete, update

sys.path.append("..")

import utilities.log as log

if not environ.get("GABBLE_DATABASE"):
    log.failure("The environment variable \"GABBLE_DATABASE\" should be set.")

    exit(1)

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
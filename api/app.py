#I might implement CORS, rate limit and JWT too.
#For CORS, see http://medium.com/@mterrano1/cors-in-a-flask-api-38051388f8cc
from flask import Flask, json

api = Flask(__name__)
json.provider.DefaultJSONProvider.sort_keys = False

from endpoints import home
from endpoints.channel import channel, create
from endpoints.conversation import conversation, create, delete
from endpoints.message import message, create, delete, edit
from endpoints.request import request, accept, decline, withdraw
from endpoints.room import room, create, delete, join, update
from endpoints.user import user, create, delete, update

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
        "error": "unsupportedtype"
    }, 415

@api.errorhandler(500)
def error_500(error):
    return {
        "success": False,
        "error": "internalservererror"
    }, 500
#I might implement CORS, rate limit and JWT too.
#For CORS, see http://medium.com/@mterrano1/cors-in-a-flask-api-38051388f8cc
from flask import Flask, request
from socket import AF_INET, SOCK_STREAM, socket

import config
from rest_api.new_endpoints import *

#Check Port:
check = socket(AF_INET, SOCK_STREAM)
try:
    check.bind(("0.0.0.0", config.rest_api.port))
except OSError:
    raise Exception("Port configured for the REST API, port number {}, is used.".format(config.rest_api.port))
finally:
    check.close()

api = Flask(__name__)

#Errors:
@api.errorhandler(404)
def error_404(parameters):
    return {
        "success": False,
        "error": "notfound"
    }, 404

@api.errorhandler(405)
def error_405(parameters):
    return {
        "success": False,
        "error": "methodnotallowed"
    }, 405
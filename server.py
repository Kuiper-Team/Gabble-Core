#https://stackoverflow.com/a/53725861
#CORS, rate limit ve JWT eklenebilir.
#CORS için http://medium.com/@mterrano1/cors-in-a-flask-api-38051388f8cc
from flask import Flask, request
from socket import AF_INET, SOCK_STREAM, socket

import config
import rest_api.new_endpoints as e

#Check if port if not busy:
check_port = socket(AF_INET, SOCK_STREAM)
try:
    check_port.bind(("0.0.0.0", config.rest_api.port))
except OSError:
    raise Exception("Port configured for the REST API, port number {}, is busy.".format(config.rest_api.port))
finally:
    check_port.close()

api = Flask(__name__)

#The Endpoint Decorator:
def fetch_parameters():
    if request.method == "GET":
        return request.args
    if request.method == "POST":
        return request.form
    else:
        return {}

#Endpoints:
@api.route("/", methods=["GET", "POST"])
def home(): e.home.route(fetch_parameters())

@api.route("/channel", methods=["GET", "POST"])
@api.route("/channel/", methods=["GET", "POST"])
def channel(): e.channel.channel.route(fetch_parameters())

@api.route("/user", methods=["GET", "POST"])
@api.route("/user/", methods=["GET", "POST"])
def user(): e.user.user.route(fetch_parameters())

#Errors:
@api.errorhandler(404)
def error_404():
    return {
        "success": False,
        "error": "notfound"
    }, 404

@api.errorhandler(405)
def error_405():
    return {
        "success": False,
        "error": "methodnotallowed"
    }, 405
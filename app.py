#I might implement CORS, rate limit and JWT too.
#And I can also switch the whole core to more professional frameworks and database management systems.
#I must add a concise permission system.
#For CORS, see http://medium.com/@mterrano1/cors-in-a-flask-api-38051388f8cc
#The REST API must have a SQL injection attack prevention system.
from flask import Flask, json

api = Flask(__name__)
json.provider.DefaultJSONProvider.sort_keys = False

#BEGINNING OF SCRIPTS CALLS
import api.endpoints.home

import api.endpoints.channel.channel
import api.endpoints.channel.create
import api.endpoints.channel.messages
import api.endpoints.channel.update_permissions

import api.endpoints.conversation.conversation
import api.endpoints.conversation.create
import api.endpoints.conversation.delete
import api.endpoints.conversation.messages

import api.endpoints.invite.invite
import api.endpoints.invite.accept
import api.endpoints.invite.create
import api.endpoints.invite.decline
import api.endpoints.invite.withdraw

import api.endpoints.message.message
import api.endpoints.message.create
import api.endpoints.message.delete
import api.endpoints.message.edit

import api.endpoints.room.room
import api.endpoints.room.create
import api.endpoints.room.delete
import api.endpoints.room.update

import api.endpoints.room.member.member
import api.endpoints.room.member.kick

import api.endpoints.user.user
import api.endpoints.user.create
import api.endpoints.user.delete
import api.endpoints.user.update

import client_adapter
#END OF SCRIPT CALLS

import utilities.log as log

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
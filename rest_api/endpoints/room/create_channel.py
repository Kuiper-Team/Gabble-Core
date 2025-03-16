import sqlite3

import database.rooms as rooms
from rest_api.presets import nouser, success, usepost

class endpoint:
    def __init__(self, arguments, controls, queries):
        self.arguments = arguments
        self.controls = controls
        self.queries = queries

    config = {
        "arguments": ("title", "uuid", "type", "settings", "permissions_map", "tags", "username", "hash", "administrator_hash"),
        "controls": {
            "access_to_room": {
                "query": False,
                "private_key": "private_key",
                "username": "username",
                "uuid": "uuid"
            },
            "asd_permission": {
                "query": False,
                "type": "type",
                "administrator_hash": "administrator_hash",
                "username": "username",
                "uuid": "uuid"
            },
            "has_permission": {
                "query": False,
                "uuid": "uuid",
                "username": "username",
                "permission": ""
            },
            "verify_hash": {
                "query": False,
                "username": "username",
                "hash": "hash"
            }
        }
    }

    def get(self):
        return usepost

    def post(self):
        uuid = self.arguments["uuid"]
        try:
            rooms.create_channel(self.arguments["title"], uuid, self.arguments["type"], self.arguments["settings"], self.arguments["permissions_map"], rooms.public_key(uuid))
        except sqlite3.OperationalError:
            return nouser
        except Exception as code:
            return {
                "success": False,
                "error": code
            }
        else:
            return success
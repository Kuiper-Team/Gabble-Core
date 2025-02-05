import sqlite3

import database.users as users
from rest_api.presets import nouser, success, usepost

class endpoint:
    def __init__(self, arguments, controls, queries):
        self.arguments = arguments
        self.controls = controls
        self.queries = queries

    config = {
        "arguments": {
            "required": ("username", "session_uuid"),
            "optional": ((),)
        },
        "controls": {
            "is_session_user_requested": {
                "query": True,
                "username": "username",
                "uuid": "session_uuid"
            },
            "session_valid": {
                "query": False,
                "uuid": "session_uuid"
            }
        }
    }

    def get(self):
        return usepost

    def post(self):
        try:
            users.delete(self.arguments["username"])
        except sqlite3.OperationalError:
            return nouser
        except Exception as code:
            return {
                "success": False,
                "error": code
            }
        else:
            return success
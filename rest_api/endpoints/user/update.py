import sqlite3

import database.session_uuids as session_uuids
import database.users as users
from rest_api.presets import nouser, success, usepost

class endpoint:
    def __init__(self, arguments, controls, queries):
        self.arguments = arguments
        self.controls = controls
        self.queries = queries

    config = {
        "arguments": ("username", "session_uuid"),
        "controls": {
            "check_booleans": {
                "query": True,
                "booleans": ("biography", "channel_settings", "display_name", "room_settings", "settings")
            },
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
        values = self.queries[0]
        try:
            users.update(self.arguments["username"], session_uuids.get_hash(self.arguments["session_uuid"]), values[0], values[1], values[2], values[3], values[4])
        except sqlite3.OperationalError:
            return nouser
        except Exception as code:
            return {
                "success": False,
                "error": code
            }
        else:
            return success
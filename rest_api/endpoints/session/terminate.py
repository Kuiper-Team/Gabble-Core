import sqlite3

from database.connection import connection, cursor
from rest_api.presets import invalidsessionuuid, success, usepost

class endpoint:
    def __init__(self, arguments, controls, queries):
        self.arguments = arguments
        self.controls = controls
        self.queries = queries

    config = {
        "arguments": {
            "required": ("session_uuid",),
            "optional": ((),)
        },
        "controls": {
            "is_session_user_requested": {
                "query": False,
                "username": "username",
                "uuid": "session_uuid"
            },
            "session_valid": {
                "query": False,
                "uuid": "session_uuid"
            },
            "user_exists": {
                "query": False,
                "users": ("username",)
            },
        }
    }

    def get(self):
        return usepost

    def post(self):
        try:
            cursor.execute("DELETE FROM session_uuids WHERE uuid = ?", (self.arguments["session_uuid"],))
        except sqlite3.OperationalError:
            return invalidsessionuuid
        else:
            connection.commit()

            return success
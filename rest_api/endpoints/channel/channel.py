import sqlite3

import database.channels as channels
from database.connection import cursor
from rest_api.presets import nochannel, usepost

class endpoint:
    def __init__(self, arguments, controls, queries):
        self.arguments = arguments
        self.controls = controls
        self.queries = queries

    config = {
        "arguments": ("username", "uuid", "session_uuid"),
        "controls": {
            "has_access_to_channel": {
                "query": False,
                "username": "username",
                "uuid": "uuid"
            },
            "is_session_user_requested": {
                "query": False,
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
            data = cursor.execute("SELECT * FROM channels WHERE uuid = ?", (self.arguments["uuid"],)).fetchone()
        except sqlite3.OperationalError:
            return nouser
        except Exception as code:
            return {
                "success": False,
                "error": code
            }
        else:
            return { #Bu, odada yetki sahibi olmayanlar içindir. Yetki sahibi olanlar için settings ve permissions_map'i de kapsayan ayrı bir return oluşturulacaktır.
                "success": True,
                "data": {
                    "title": data[0],
                    "room_uuid": data[2],
                    "type": data[3],
                    "tags": data[6]
                }
            }

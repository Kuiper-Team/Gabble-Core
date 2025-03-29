import database.rooms as rooms
from api import usepost

class endpoint:
    def __init__(self, arguments, controls, queries):
        self.arguments = arguments
        self.controls = controls
        self.queries = queries

    config = {
        "arguments": ("uuid", "username", "hash", "private_key"),
        "controls": {
            "access_to_room": {
                "query": False,
                "private_key": "private_key",
                "username": "username",
                "uuid": "uuid"
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
        try:
            rooms.add_member(self.arguments["username"], self.arguments["uuid"], self.arguments["private_key"])
        except Exception as code:
            return {
                "success": False,
                "error": code
            }
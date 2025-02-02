import database.users as users
import database.session_uuids as session_uuids
from rest_api.presets import incorrectpassword, usepost

class endpoint:
    def __init__(self, arguments, queries):
        self.arguments = arguments
        self.controls = queries

    config = {
        "arguments": {
            "required": ("username", "password", "expiry"),
            "optional": ((),)
        },
        "controls": {
            "user_exists": {
                "query": False,
                "users": ("username",)
            },
            "valid_session_expiry": {
                "query": False,
                "expiry": "expiry"
            }
        }
    }

    def get(self):
        return usepost

    def post(self):
        check, hash = users.check_credentials(self.arguments["username"], self.arguments["password"])
        if check:
            try:
                session_uuid = session_uuids.create(self.arguments["username"], self.arguments["expiry"], hash)
            except Exception as code:
                return {
                    "success": False,
                    "error": code
                }
            else:
                return {
                    "success": True,
                    "uuid": session_uuid
                }
        else:
            return incorrectpassword

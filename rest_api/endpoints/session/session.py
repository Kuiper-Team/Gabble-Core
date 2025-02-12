import database.session_uuids as session_uuids

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
            "session_valid": {
                "query": False,
                "uuid": "session_uuid"
            }
        }
    }

    def get(self):
        try:
            expiry = session_uuids.check(self.arguments["session_uuid"])[1]
        except Exception as code:
            return {
                "success": False,
                "error": code
            }
        else:
            return {
                "expiry": expiry
            }

    def post(self):
        return self.get()

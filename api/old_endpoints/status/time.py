from datetime import datetime
import utilities.generation as generation

class endpoint:
    def __init__(self, arguments, controls, queries):
        self.arguments = arguments
        self.controls = controls
        self.queries = queries

    config = {
        "arguments": ("timestamp"),
        "controls": {
            "is_integer": {
                "query": False,
                "argument": "timestamp"
            }
        }
    }

    def get(self):
        now = datetime.now()
        return {
            "server_time": {
                "unix": generation.unix_timestamp(now),
                "standard": now
            },
            "ping": now - (self.arguments["timestamp"] * 1000)
        }

    def post(self):
        return self.get()
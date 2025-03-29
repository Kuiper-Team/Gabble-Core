import os

from config import rest_api
from api import unrecognizedlocale, useget


class endpoint:
    def __init__(self, arguments, controls, queries):
        self.arguments = arguments
        self.controls = controls
        self.queries = queries

    config = {
        "arguments": ("locale", "session_uuid")
    }

    def get(self):
        locale = self.arguments("locale")
        if locale in ("arabic", "english", "japanese", "turkish"):
            content = open(os.path.join(rest_api.incidents_path, locale + ".txt"), "r", encoding="utf-8")
            return {
                "success": True,
                "incident": content
            }
        else:
            return unrecognizedlocale

    def post(self):
       return useget
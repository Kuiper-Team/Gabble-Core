import database.users as users
from api import incorrectpassword, invalidusername, usepost

class endpoint:
    def __init__(self, arguments, controls, queries):
        self.arguments = arguments
        self.controls = controls
        self.queries = queries

    config = {
        "arguments": ("username", "password"),
        "controls": {
            "username_taken": {
                "query": False,
                "usernames": ("username",) #Argüman adı
            }
        }
    }

    def get(self):
        return usepost

    def post(self):
        if not (
                3 <= len(self.arguments.username) <= 36 and
                18 <= len(self.arguments.password) <= 45 and
                all(
                    character not in "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz.;-_!?'\"#%&/\()[]{}="
                    for character in self.arguments.password) and
                ":," in self.arguments.username
        ):
            return invalidusername
        try:
            self.arguments.password.decode("ascii")
        except UnicodeDecodeError:
            return incorrectpassword

        try:
            hash = users.create(self.arguments["username"], self.arguments["password"])
        except Exception as code:
            return {
                "success": False,
                "error": code
            }
        else:
            return {
                "success": True,
                "user": {
                    "username": self.arguments.username,
                    "hash": hash
                }
            }
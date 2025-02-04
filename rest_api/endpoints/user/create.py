import database.session_uuids as session_uuids
import database.users as users
import utilities.generation as generation
from rest_api.presets import nouser, usepost

class endpoint:
    def __init__(self, arguments, controls, queries):
        self.arguments = arguments
        self.controls = controls
        self.queries = queries

    config = {
        "arguments": {
            "required": ("username", "password"),
            "optional": ((),)
        },
        "controls": {
            "username_taken": {
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
            return {
                "success": False,
                "error": "invalidusername"
            }
        try:
            self.arguments.password.decode("ascii")
        except UnicodeDecodeError:
            return {
                "success": False,
                "error": "invalidpassword"
            }

        try:
            hash = users.create(self.arguments["username"], self.arguments["password"])
        except Exception as code:
            return {
                "success": False,
                "error": code
            }
        else:
            try:
                session_uuids.create(self.arguments.username, generation.unix_timestamp(datetime.now()) + 86400, hash) #İlk oturum açılışında 1 gün süre verilir.
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
                        "hash": generation.hashed_password(self.arguments.password)
                    }
                }
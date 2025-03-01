import utilities.generation as generation
from rest_api.presets import usepost

class endpoint:
    def __init__(self, arguments, controls, queries):
        self.arguments = arguments
        self.controls = controls
        self.queries = queries

    config = {
        "arguments": ("uuid", "username", "private_key", "administrator_hash"),
        "controls": {
            "access_to_room": {
                "query": False, #rooms konusunda herkese açık olarak bakılabilecek pek veri yoktur.
                "private_key": "private_key",
                "username": "username",
                "uuid": "uuid"
            },
            "asd_permission": {
                "query": True,
                "type": "type",
                "administrator_hash": "administrator_hash",
                "username": "username",
                "uuid": "uuid"
            },
            "fetch_from_db": {
                "query": True,
                "table": "rooms",  # Doğrudan tablo adı
                "row": "uuid",  # Doğrudan satır adı
                "where": "uuid"  # Argüman adı
            }
        }
    }

    def get(self):
        return usepost

    def post(self):
        data = self.queries["fetch_from_db"]
        administrator_hash = self.arguments["administrator_hash"]
        private_key = self.arguments["private_key"]
        type = data[3]
        if self.queries[1]:
            return {
                "success": True,
                "data": {
                    "insensitive": {
                        "title": generation.rsa_decrypt(data[0], private_key),
                        "type": type,
                        "channels": data[4],
                        "members": data[5],
                    },
                    "sensitive": {
                        "public_key": data[2],
                        "settings": generation.rsa_decrypt(data[6], private_key) if type == 0 else generation.aes_decrypt(data[6], administrator_hash),
                        "permission_map": generation.rsa_decrypt(data[7], private_key) if type == 0 else generation.aes_decrypt(data[7], administrator_hash)
                    }
                },
            }
        else:
            return {
                "success": True,
                "data": {
                    "insensitive": {
                        "title": generation.rsa_decrypt(data[0], private_key),
                        "type": type,
                        "channels": data[4],
                        "members": data[5],
                    }
                }
            }
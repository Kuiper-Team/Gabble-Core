import sqlite3

import utilities.generation as generation
from database.connection import cursor
from rest_api.presets import nouser, usepost
from utilities.generation import rsa_decrypt


class endpoint:
    def __init__(self, arguments, controls, queries):
        self.arguments = arguments
        self.controls = controls
        self.queries = queries

    config = {
        "arguments": ("uuid", "username", "private_key"),
        "controls": {
            "fetch_from_db": {
                "query": True,
                "table": "rooms", #Doğrudan tablo adı
                "row": "uuid", #Doğrudan satır adı
                "where": "uuid" #Argüman adı
            },
            "access_to_room": {
                "query": False, #rooms konusunda herkese açık olarak bakılabilecek pek veri yoktur.
                "private_key": "private_key",
                "username": "username",
                "uuid": "uuid"
            },
            "administrator_hash": {
                "query": True,
                "hash": "administrator_hash"
            },
            "asd_permission": {
                "query": True,
                "private_key": "private_key",
                "username": "username",
                "uuid": "uuid"
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
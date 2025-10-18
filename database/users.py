import json
from base64 import b64encode
from hashlib import sha256

import database.conversations as conversations
import database.rooms as rooms
import database.sqlite_wrapper as sql
import utilities.cryptography as cryptography
from utilities.uuidv7 import uuid_v7

table = "users"

sql.table(table,
    (
        sql.C("user_id", sql.Types.TEXT, not_null=True),
        sql.C("display_name", sql.Types.TEXT, not_null=True),
        sql.C("salt_b64", sql.Types.TEXT, not_null=True),
        sql.C("biography", sql.Types.TEXT, not_null=True),
        sql.C("private", sql.Types.TEXT, not_null=True)
    ),
    primary_key="user_id"
)

def create(user_id, password):
    hash, salt = cryptography.argon2_hash(password)
    salt = b64encode(salt).decode()
    sql.insert(table,
        (
            user_id,
            b64encode(user_id),
            salt,
            "",
            sha256(user_id.encode()).hexdigest(),
            cryptography.aes_encrypt(json.dumps(
                {
                    "discriminator": uuid_v7().hex, #This works as a unique salt to prevent attacks and has no other use.
                    "settings": {
                        #User preferences
                        "preferences_channels": {
                            # Channel-specific preferences
                        },
                        "preferences_conversations": {
                            # Conversation-specific preferences
                        },
                        "preferences_rooms": {
                            #Room-specific preferences
                        }
                    },
                    "connections": {}, #Format -> user_id: contact_name (Empty string if not specified)
                    "key_chain": {}, #Format -> room_uuid: private_key
                    "inbox": {} #Format -> notification_uuid: { timestamp: timestamp (must be UTC), subject: user_id (can be "system" or something like that), body: body }
                },
            ), hash)
        ),
        exception="userexists"
    )

    return salt

def delete(user_id, hash):
    key_chain: dict = private(user_id, hash)["key_chain"]
    for room_uuid in key_chain:
        try:
            private_key = key_chain[user_id]

            if user_id in rooms.members(room_uuid, private_key):
                rooms.kick_member(user_id, room_uuid, private_key)

            if sql.select("conversations", "user_id", user_id, safe=True)[0] is not None:
                conversations.delete(user_id)

        except Exception("noroom"): pass
        except Exception("noconversation"): pass

    sql.delete(table, "user_id", user_id, exception="nouser")

def update(user_id, display_name=None, biography=None, preferences=None, preferences_channels=None, preferences_conversations=None, preferences_rooms=None):
    sql.update(table, "display_name", display_name, "user_id", user_id, condition=display_name, exception="nouser")
    sql.update(table, "biography", biography, "user_id", user_id, condition=biography, exception="nouser")
    sql.update(table, "preferences", preferences, "username", user_id, condition=preferences, exception="nouser")
    sql.update(table, "preferences_channels", preferences_channels, "user_id", user_id, condition=preferences_channels, exception="nouser")
    sql.update(table, "preferences_conversations", preferences_conversations, "user_id", user_id, condition=preferences_conversations, exception="nouser")
    sql.update(table, "preferences_rooms", preferences_rooms, "user_id", user_id, condition=preferences_rooms, exception="nouser")

def exists(user_id):
    data = sql.select(table, "user_id", user_id, safe=True)

    return data is not None

def add_connection():
    pass

def remove_connection():
    pass

def private(user_id, hash) -> dict:
    data = cryptography.aes_decrypt(sql.select(table, "user_id", user_id, column="private", exception="nouser")[0], hash)

    return json.loads(data)
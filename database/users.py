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
        sql.C("username", sql.Types.TEXT, not_null=True),
        sql.C("uuid", sql.Types.TEXT, not_null=True),
        sql.C("salt_b64", sql.Types.TEXT, not_null=True),
        sql.C("biography", sql.Types.TEXT, not_null=True),
        sql.C("request_hash", sql.Types.TEXT, not_null=True),
        sql.C("private", sql.Types.TEXT, not_null=True)
    ),
    primary_key="uuid"
)

def create(username, password):
    hash, salt = cryptography.argon2_hash(password)
    print(hash, salt) #DEBUGGING
    uuid = uuid_v7().hex
    sql.insert(table,
        (
            username,
            uuid,
            b64encode(salt).decode(),
            "",
            sha256(uuid.encode()).hexdigest(),
            cryptography.aes_encrypt(json.dumps(
                {
                    "discriminator": uuid_v7().hex, #This works as a unique salt to prevent attacks. No other use.
                    "settings": {
                        #…
                        "rooms": {
                            #…
                        },
                        "channels": {
                          #…
                        }
                    },
                    "connections": {}, #Format -> user_uuid: display_name
                    "key_chain": {}, #Format -> room_uuid: private_key
                    "inbox": {} #Format -> notification_inbox
                },
            ), hash)
        ),
        exception="couldnotperform"
    )

    return uuid, salt, hash.hex()

def delete(uuid, hash):
    key_chain = private(uuid, hash)["key_chain"]
    for room_uuid in object:
        try:
            private_key = object[uuid]

            if uuid in rooms.members(room_uuid, private_key):
                rooms.kick_member(uuid, room_uuid, private_key)

            if sql.select("conversations", "uuid", uuid, column="uuid", safe=True)[0] is not None:
                conversations.delete(uuid)

        except Exception("noroom"): pass
        except Exception("noconversation"): pass

    sql.delete(table, "uuid", uuid, exception="nouser")

#INCLUDE USERNAME THIS TIME
def update(username, display_name=None, settings=None, room_settings=None, channel_settings=None, biography=None):
    sql.update(table, "display_name", display_name, "username", username, condition=display_name, exception="nouser")
    sql.update(table, "settings", settings, "username", username, condition=settings, exception="nouser")
    sql.update(table, "room_settings", room_settings, "username", username, condition=room_settings, exception="nouser")
    sql.update(table, "channel_settings", channel_settings, "username", username, condition=channel_settings, exception="nouser")
    sql.update(table, "biography", biography, "username", username, condition=biography, exception="nouser")

def exists(uuid):
    data = sql.select(table, "uuid", uuid, safe=True)

    return data is not None

def add_connection():
    pass

def remove_connection():
    pass

def append_to_key_chain(username, hash, label, key):
    pass

def delete_from_key_chain(username, hash, label):
    pass

def append_to_inbox(username, hash, label, key):
    pass

def delete_from_inbox(username, hash, label):
    pass

def private(uuid, hash) -> dict:
    data = cryptography.aes_decrypt(sql.select(table, "uuid", uuid, exception="nouser")[0], hash)

    return json.loads(data)
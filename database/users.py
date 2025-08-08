import json
from base64 import b64encode
from hashlib import sha256

import database.conversations as conversations
import database.rooms as rooms
import database.sqlite_wrapper as sql
import utilities.cryptography as cryptography

table = "users"

sql.table(table,
    (
        sql.C("username", sql.Types.TEXT, not_null=True),
        sql.C("display_name", sql.Types.TEXT, not_null=True),
        sql.C("salt_b64", sql.Types.TEXT, not_null=True),
        sql.C("settings", sql.Types.TEXT, not_null=True),
        sql.C("room_settings", sql.Types.TEXT, not_null=True),
        sql.C("channel_settings", sql.Types.TEXT, not_null=True),
        sql.C("friends", sql.Types.TEXT, not_null=True), #Will be converted to JSON
        sql.C("biography", sql.Types.TEXT),
        sql.C("request_hash", sql.Types.TEXT, not_null=True),
        sql.C("inbox", sql.Types.TEXT, not_null=True),
        sql.C("key_chain", sql.Types.TEXT, not_null=True),
    ),
    primary_key="username"
)

default_settings = json.dumps(
    {
        "icon": 0
    }
)

default_room_settings = json.dumps(
    {

    }
)

default_channel_settings = json.dumps(
    {
        "title": "channel"
    }
)

def create(username, password):
    hash, salt = cryptography.argon2_hash(password)
    sql.insert(table,
        (
            username,
            username,
            b64encode(salt).decode(),
            cryptography.aes_encrypt(default_settings, hash),
            cryptography.aes_encrypt(default_room_settings, hash),
            cryptography.aes_encrypt(default_channel_settings, hash),
            None,
            None,
            sha256(username.encode()).hexdigest(),
            cryptography.aes_encrypt("{}", hash),
            cryptography.aes_encrypt("{}", hash)
        ),
        exception="userexists"
    )

    return hash.hexdigest()

def delete(username, hash):
    object = key_chain(username, hash)
    for uuid in object:
        try:
            private_key = object[uuid]

            if username in rooms.members(uuid, private_key):
                rooms.kick_member(username, uuid, private_key)

            if sql.select("conversations", "uuid", uuid, column="uuid", safe=True)[0] is not None:
                conversations.delete(uuid)

        except Exception("noroom"): pass
        except Exception("noconversation"): pass

    sql.delete(table, "username", username, exception="nouser")

def friends(username, hash, list=True):
    encrypted = sql.select(table, "username", username, column="friends", exception="nouser")[0]
    decrypted = cryptography.aes_decrypt(encrypted, hash)

    return decrypted.split(",") if list else decrypted

def add_friends(username_1, username_2, hash_1, hash_2):
    friends_1 = friends(username_1, hash_1)
    friends_2 = friends(username_2, hash_2)

    new_encrypted_1 = cryptography.aes_encrypt(friends_1 + "," + username_2, hash_1)
    new_encrypted_2 = cryptography.aes_encrypt(friends_2 + "," + username_1, hash_2)

    sql.update(table, "friends", new_encrypted_1, "username", username_1, exception="nouser")
    sql.update(table, "friends", new_encrypted_2, "username", username_2, exception="nouser")

def update(username, display_name=None, settings=None, room_settings=None, channel_settings=None, biography=None):
    sql.update(table, "display_name", display_name, "username", username, condition=display_name, exception="nouser")
    sql.update(table, "settings", settings, "username", username, condition=settings, exception="nouser")
    sql.update(table, "room_settings", room_settings, "username", username, condition=room_settings, exception="nouser")
    sql.update(table, "channel_settings", channel_settings, "username", username, condition=channel_settings, exception="nouser")
    sql.update(table, "biography", biography, "username", username, condition=biography, exception="nouser")

def exists(username):
    data = sql.select(table, "username", username, safe=True)

    return data is not None

def key_chain(username, hash):
   object = cryptography.aes_decrypt(sql.select(table, "username", username, column="key_chain", exception="nouser")[0], hash)

    return json.loads(object)

def append_to_key_chain(username, hash, label, key):
    try:
        object = key_chain(username, hash)
    except Exception as code:
        raise Exception(code)
    else:
        json_data = json.dumps(object.update({label: key}))

        sql.update(table, "key_chain", json_data, "username", username)

def delete_from_key_chain(username, hash, label):
    try:
        object = key_chain(username, hash)
    except Exception as code:
        raise Exception(code)
    else:
        json_data = json.dumps(object.pop(label))

        sql.update(table, "key_chain", json_data, "username", username)

def inbox(username, hash):
    dictionary = cryptography.aes_decrypt(sql.select(table, "username", username, column="inbox", exception="nouser")[0], hash)

    return json.loads(dictionary)

def append_to_inbox(username, hash, label, key):
    try:
        dictionary = key_chain(username, hash)
    except Exception as code:
        raise Exception(code)
    else:
        json_data = json.dumps(dictionary.update({label: key}))

        sql.update(table, "inbox", json_data, "username", username)

def delete_from_inbox(username, hash, label):
    try:
        dictionary = key_chain(username, hash)
    except Exception as code:
        raise Exception(code)
    else:
        json_data = json.dumps(dictionary.pop(label))

        sql.update(table, "inbox", json_data, "username", username)
import json
import pyargon2
import sqlite3
from hashlib import sha256

import database.conversations as conversations
import database.rooms as rooms
import utilities.generation as generation
from database.connection import connection, cursor

cursor.execute("""CREATE TABLE IF NOT EXISTS users (
username TEXT NOT NULL,
display_name TEXT NOT NULL,
settings TEXT NOT NULL,
room_settings TEXT NOT NULL,
channel_settings TEXT NOT NULL,
friends TEXT,
biography TEXT,
request_hash TEXT NOT NULL,
inbox TEXT NOT NULL,
key_chain TEXT NOT NULL,
PRIMARY KEY (username))
""")

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
    salt = generation.random_string(16)
    hash = pyargon2.hash(password, salt, hash_len=16)
    key_hash = sha256((salt + hash).encode())
    key = key_hash.digest()
    try:
        cursor.execute("INSERT INTO users VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                username,
                username,
                generation.aes_encrypt(default_settings, key),
                generation.aes_encrypt(default_room_settings, key),
                generation.aes_encrypt(default_channel_settings, key),
                None,
                None,
                sha256(username.encode()).hexdigest(),
                generation.aes_encrypt("{}", key),
                generation.aes_encrypt("{}", key)
            )
        )
    except sqlite3.OperationalError:
        raise Exception("userexists")
    else:
        connection.commit()

        return key_hash.hexdigest()

def delete(username, hash):
    object = key_chain(username, hash)
    for uuid in object:
        try:
            private_key = object[uuid]

            if username in rooms.members(uuid, private_key):
                rooms.kick_member(username, uuid, private_key)

            try:
                cursor.execute("SELECT uuid FROM conversations WHERE uuid = ?", (uuid,)).fetchone()[0]
            except sqlite3.OperationalError:
                pass
            else:
                conversations.delete(uuid)

        except Exception("noroom"): pass
        except Exception("noconversation"): pass

    try:
        cursor.execute("DELETE FROM users WHERE username = ?", (username,))
    except sqlite3.OperationalError:
        raise Exception("nouser")
    else:
        connection.commit()

def friends(username, hash, list=True):
    try:
        encrypted = cursor.execute("SELECT friends FROM users WHERE username = ?", (username,)).fetchone()[0]
    except sqlite3.OperationalError:
        raise Exception("nouser")
    else:
        decrypted = generation.aes_decrypt(encrypted, hash)

        return decrypted.split(",") if list else decrypted

def add_friends(username_1, username_2, hash_1, hash_2):
    try:
        friends_1 = friends(username_1, hash_1)
        friends_2 = friends(username_2, hash_2)
    except sqlite3.OperationalError:
        raise Exception("nouser")
    else:
        new_encrypted_1 = generation.aes_encrypt(friends_1 + "," + username_2, hash_1)
        new_encrypted_2 = generation.aes_encrypt(friends_2 + "," + username_1, hash_2)
        cursor.execute("INSERT OR REPLACE INTO users (friends) VALUES(?) WHERE username = ?", (new_encrypted_1, username_1))
        cursor.execute("INSERT OR REPLACE INTO users (friends) VALUES(?) WHERE username = ?", (new_encrypted_2, username_2))
        connection.commit()

def update(username, display_name=None, settings=None, room_settings=None, channel_settings=None, biography=None):
    if display_name:
        try:
            cursor.execute("UPDATE users SET display_name = ? WHERE username = ?", (display_name, username))
        except sqlite3.OperationalError:
            raise Exception("nouser")
        else:
            connection.commit()
    if settings:
        try:
            cursor.execute("UPDATE users SET settings = ? WHERE username = ?", (settings, username))
        except sqlite3.OperationalError:
            raise Exception("nouser")
        else:
            connection.commit()
    if room_settings:
        try:
            cursor.execute("UPDATE users SET room_settings = ? WHERE username = ?", (room_settings, username))
        except sqlite3.OperationalError:
            raise Exception("nouser")
        else:
            connection.commit()
    if channel_settings:
        try:
            cursor.execute("UPDATE users SET channel_settings = ? WHERE username = ?", (channel_settings, username))
        except sqlite3.OperationalError:
            raise Exception("nouser")
        else:
            connection.commit()
    if biography:
        try:
            cursor.execute("UPDATE users SET channel_settings = ? WHERE username = ?", (biography, username))
        except sqlite3.OperationalError:
            raise Exception("nouser")
        else:
            connection.commit()

def exists(username):
    try:
        username = cursor.execute("SELECT username FROM users WHERE username = ?", (username,)).fetchone()
    except sqlite3.OperationalError:
        return False
    else:
        return username is not None

def key_chain(username, hash):
    try:
       object = generation.aes_decrypt(cursor.execute("SELECT key_chain FROM users WHERE username = ?", (username,)).fetchone()[0], hash)
    except sqlite3.OperationalError:
        raise Exception("nouser")
    else:
        return json.loads(object)

def append_to_key_chain(username, hash, label, key):
    try:
        object = key_chain(username, hash)
    except Exception as code:
        raise Exception(code)
    else:
        json_data = json.dumps(object.update({label: key}))
        cursor.execute("UPDATE users SET key_chain = ? WHERE username = ?", (json_data, username))

        connection.commit()

def delete_from_key_chain(username, hash, label):
    try:
        object = key_chain(username, hash)
    except Exception as code:
        raise Exception(code)
    else:
        json_data = json.dumps(object.pop(label))
        cursor.execute("UPDATE users SET key_chain = ? WHERE username = ?", (json_data, username))

        connection.commit()

def inbox(username, hash):
    try:
       dictionary = generation.aes_decrypt(cursor.execute("SELECT inbox FROM users WHERE username = ?", (username,)).fetchone()[0], hash)
    except sqlite3.OperationalError:
        raise Exception("nouser")
    else:
        return json.loads(dictionary)

def append_to_inbox(username, hash, label, key):
    try:
        dictionary = key_chain(username, hash)
    except Exception as code:
        raise Exception(code)
    else:
        json_data = json.dumps(dictionary.update({label: key}))
        cursor.execute("UPDATE users SET inbox = ? WHERE username = ?", (json_data, username))

        connection.commit()

def delete_from_inbox(username, hash, label):
    try:
        dictionary = key_chain(username, hash)
    except Exception as code:
        raise Exception(code)
    else:
        json_data = json.dumps(dictionary.pop(label))
        cursor.execute("UPDATE users SET inbox = ? WHERE username = ?", (json_data, username))

        connection.commit()
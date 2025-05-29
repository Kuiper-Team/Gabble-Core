import json
import sqlite3

import database.rooms as rooms
import database.users as users
import utilities.generation as generation
from database.connection import cursor

def access_to_channel(username, uuid, private_key): #Encompasses conversations.
    pass

def access_to_room(username, uuid, private_key):
    if username in rooms.members(uuid, private_key):
        return True
    else:
        return False

def check_parameters(parameters, requested):
    for parameter in requested:
        try:
            parameters[parameter]
        except KeyError:
            return False

    return True

def fetch_from_db(table, where, value, column="*"):
    try:
        data = cursor.execute("SELECT ? FROM ? WHERE ? = ?", (column, table, where, value)).fetchone()
    except sqlite3.OperationalError:
        return None
    else:
        return data

def fetch_invite_result(uuid, passcode, list=True):
    try:
        result = cursor.execute("SELECT result FROM invites WHERE uuid = ?", (uuid,)).fetchone()[0]
    except sqlite3.OperationalError:
        return None
    else:
        return result.split(",") if list else result

def user_exists(username):
    return users.exists(username)

def verify_hash(username, hash):
    try:
        json.loads(generation.aes_decrypt(cursor.execute("SELECT key_chain FROM user WHERE username = ?", (username,)).fetchone()[0], hash))
    except Exception:
        return False

def verify_passcode(uuid, passcode):
    try:
        result = generation.aes_decrypt(cursor.execute("SELECT result FROM invites WHERE uuid = ?", (uuid,)).fetchone()[0], passcode)
    except Exception:
        return False
    else:
        return result.isascii() and len(result) == 3

def verify_private_key(uuid, private_key):
    try:
        title = generation.rsa_decrypt(cursor.execute("SELECT title FROM rooms WHERE uuid = ?", (uuid,)).fetchone()[0], private_key)
    except Exception:
        return False
    else:
        return title.isascii()
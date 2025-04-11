#Format validation function should be coded inside utilities/validation.py!
import json
import sqlite3

import database.rooms as rooms
import database.users as users
import utilities.generation as generation
import utilities.validation as validation
from database.connection import cursor

def access_to_channel(username, uuid, private_key):
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

def fetch_from_db(table, where, value):
    try:
        data = cursor.execute("SELECT * FROM ? WHERE ? = ?", (table, where, value)).fetchone()[0]
    except sqlite3.OperationalError:
        return None
    else:
        return data

def has_permissions(username, uuid, permissions, administrator_hash):
    return rooms.has_permissions(uuid, username, permissions, administrator_hash)

def user_exists(username):
    return users.exists(username)

def verify_administrator_hash(uuid, administrator_hash):
    try:
        settings = json.loads(generation.aes_decrypt(cursor.execute("SELECT settings FROM rooms WHERE uuid = ?", (uuid,)), administrator_hash))
    except Exception:
        return False
    else:
        return True

def verify_hash(username, hash):
    try:
        json.loads(generation.aes_decrypt(cursor.execute("SELECT key_chain FROM user WHERE username = ?", (username)).fetchone()[0], hash))
    except Exception:
        return False

def verify_private_key(uuid, private_key):
    try:
        title = generation.rsa_decrypt(cursor.execute("SELECT title FROM rooms WHERE uuid = ?", (uuid,)), private_key)
    except Exception:
        return False
    else:
        return title.isascii()
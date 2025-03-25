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
    pass

def asd_permission(username, uuid, private_key):
    pass

def check_arguments(arguments, requested):
    for argument in requested:
        if arguments[argument] is None: return argument

    return ""

def fetch_from_db(arguments, table, row, where):
    try:
        data = cursor.execute("SELECT * FROM ? WHERE ? = ?", (table, row, arguments[where])).fetchone()[0]
    except sqlite3.OperationalError:
        return None
    else:
        return data

def has_permission(arguments, username, uuid, permission, administrator_hash):
    return rooms.has_permissions(uuid, username, permission, arguments[administrator_hash])

def is_integer(arguments, argument):
    return validation.integer(arguments[argument])

def is_username_taken(username):
    return users.exists(username)

def is_uuid(arguments, argument, version):
    return validation.uuid(arguments[argument], version)

def verify_hash(arguments, username, hash):
    try:
        try:
            key_chain = cursor.execute("SELECT key_chain FROM user WHERE username = ?", (arguments[username],)).fetchone()[0]
        except sqlite3.OperationalError:
            return False
        else:
            json.loads(generation.aes_decrypt(key_chain, arguments[hash]))
    except ValueError:
        return False
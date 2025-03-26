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

def check_parameters(parameters, requested):
    for argument in requested:
        if parameters[argument] is None: return argument

    return ""

def fetch_from_db(parameters, table, where, value_parameter):
    try:
        data = cursor.execute("SELECT * FROM ? WHERE ? = ?", (table, where, parameters[value_parameter])).fetchone()[0]
    except sqlite3.OperationalError:
        return None
    else:
        return data

def has_permission(parameters, username, uuid, permission, administrator_hash):
    return rooms.has_permissions(uuid, username, permission, parameters[administrator_hash])

def is_integer(parameters, argument):
    return validation.integer(parameters[argument])

def is_uuid(parameters, argument, version):
    return validation.uuid(parameters[argument], version)

def user_exists(username):
    return users.exists(username)

def verify_hash(parameters, username, hash):
    try:
        try:
            key_chain = cursor.execute("SELECT key_chain FROM user WHERE username = ?", (parameters[username],)).fetchone()[0]
        except sqlite3.OperationalError:
            return False
        else:
            json.loads(generation.aes_decrypt(key_chain, parameters[hash]))
    except ValueError:
        return False
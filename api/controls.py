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

def access_to_sensitive_data(uuid, administrator_hash):
    try:
        result = cursor.execute("SELECT administrator_hash FROM rooms WHERE uuid = ?", (uuid,))
    except sqlite3.OperationalError:
        return False

    return administrator_hash == result

def check_parameters(parameters, requested):
    for parameter in requested:
        try:
            parameters[parameter]
        except KeyError:
            return False

    return True

def fetch_from_db(parameters, table, where, value_parameter):
    try:
        data = cursor.execute("SELECT * FROM ? WHERE ? = ?", (table, where, parameters[value_parameter])).fetchone()[0]
    except sqlite3.OperationalError:
        return None
    else:
        return data

def has_permissions(parameters, username, uuid, permissions, administrator_hash):
    return rooms.has_permissions(uuid, username, permissions, parameters[administrator_hash])

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
import sqlite3
from calendar import isleap
from datetime import datetime
from uuid import UUID

import generation
from config import messages
from database.connection import connection, cursor

def uuid_v4(uuid_str):
    object = None
    try:
        object = UUID(uuid_str)
    except ValueError:
        return False

    return object.version == 4

def uuid_v7(uuid_str):
    object = None
    try:
        object = UUID(uuid_str)
    except ValueError:
        return False

    return object.version == 7

def message_id(message):
    try:
        length = len(message)
        if (
            64 < length <= messages.character_limit + 64 and
            uuid_v7(message[:33]) and
            uuid_v7(message[33:65])
        ):
            return True
        else:
            return False
    except ValueError:
        return False

def timestamp(timestamp):
    return timestamp > generation.unix_timestamp(datetime.now())

def check_credentials(username, password):
    try:
        return generation.hashed_password(password) == cursor.execute("SELECT hash FROM users WHERE username = ?", (username,)).fetchone()[0]
    except sqlite3.OperationalError:
        raise Exception("nouser")

def check_session_uuid(uuid):
    try:
        expiry = cursor.execute("SELECT expiry FROM session_uuids WHERE uuid = ?", (uuid,)).fetchone()[0]

        return timestamp(expiry)
    except sqlite3.OperationalError:
        return False

def uuid_timestamp_to_unix(uuid):
    pass #Hazır değil.
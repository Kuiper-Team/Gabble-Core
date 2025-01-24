import sqlite3
from calendar import isleap
from datetime import datetime
from uuid import UUID

import generation
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
        hours = int(message[:2])
        minutes = int(message[2:4])
        month = int(message[6:8])
        day = int(message[4:6])

        day_max = None
        if month in [1, 3, 5, 7, 8, 10, 12]: day_max = 31
        elif month in [4, 6, 9, 11]: day_max = 30
        elif month == 2: day_max = 29 if isleap(message[6:8]) else 28
        else: return False

        if (
            len(message) > 44 and
            all(character in "0123456789" for character in message[:12]) and
            not any(not character for character in message[:12]) and
            0 <= hours < 24 and
            0 <= minutes < 60 and
            1 <= month <= 12 and
            0 < day <= day_max and
            uuid_v4("{}-{}-{}-{}-{}".format(message[12:20], message[20:24], message[24:28], message[28:32], message[32:44]))
        ): return True
        else: return False
    except ValueError:
        return False

def timestamp(timestamp):
    return timestamp > generation.unix_timestamp(datetime.now())

def check_credentials(username, password):
    try:
        return generation.hashed_password(password) == cursor.execute("SELECT hash FROM users WHERE username = ?", (username,)).fetchone()[0]
    except sqlite3.OperationalError:
        raise Exception("nouser")

def check_session_uuid(session_uuid):
    try:
        expiry = cursor.execute("SELECT expiry FROM session_uuids WHERE uuid = ?", (session_uuid,)).fetchone()[0]

        return timestamp(expiry)
    except sqlite3.OperationalError:
        return False

def uuid_timestamp_to_unix(uuid):
    pass #Hazır değil.
import sqlite3
import sys
from datetime import datetime

sys.path.append("..")

import utilities.generation as generation
from database.connection import connection, cursor
from utilities.uuidv7 import uuid_v7

cursor.execute("""CREATE TABLE IF NOT EXISTS messages (
message TEXT NOT NULL,
uuid TEXT NOT NULL,
room_uuid TEXT,
channel_uuid TEXT NOT NULL,
timestamp TEXT NOT NULL,
PRIMARY KEY (uuid))
"""
)

def create(message, room_uuid, channel_uuid, public_key):
    try:
        cursor.execute("INSERT INTO messages VALUES (?, ?, ?, ?, ?)", (generation.rsa_encrypt(message, public_key), uuid_v7().hex, room_uuid, channel_uuid, generation.rsa_encrypt(generation.unix_timestamp(datetime.now())), public_key))
    except sqlite3.OperationalError:
        raise Exception("couldntinsert")
    else:
        connection.commit()

def delete(uuid, room_uuid, channel_uuid):
    try:
        cursor.execute("DELETE FROM messages WHERE uuid = ? AND room_uuid = ? AND channel_uuid = ?", (uuid, room_uuid, channel_uuid))
    except sqlite3.OperationalError:
        raise Exception("nomessage")
    else:
        connection.commit()

def edit(new_message, uuid, room_uuid, channel_uuid):
    try:
        cursor.execute("UPDATE messages SET new_message = ? WHERE uuid = ? AND room_uuid = ? AND channel_uuid = ?", (generation.aes_encrypt(new_message, hash), uuid, room_uuid, channel_uuid))
    except sqlite3.OperationalError:
        raise Exception("nomessage")
    else:
        connection.commit()
import sqlite3
import sys
from datetime import datetime

sys.path.append("..")

import database.channels as channels
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

def create(message, channel_uuid, public_key):
    try:
        uuid = uuid_v7().hex
        timestamp = generation.unix_timestamp(datetime.now())
        cursor.execute("INSERT INTO messages VALUES (?, ?, ?, ?, ?)", (generation.rsa_encrypt(message, public_key), uuid, channels.room_of(channel_uuid), channel_uuid, generation.rsa_encrypt(timestamp, public_key)), public_key)
    except sqlite3.OperationalError:
        raise Exception("couldntinsert")
    else:
        connection.commit()

    return uuid, timestamp

def delete(uuid, channel_uuid):
    try:
        cursor.execute("DELETE FROM messages WHERE uuid = ? AND room_uuid = ? AND channel_uuid = ?", (uuid, channels.room_of(channel_uuid), channel_uuid))
    except sqlite3.OperationalError:
        raise Exception("nomessage")
    else:
        connection.commit()

def edit(new_message, uuid, channel_uuid):
    try:
        cursor.execute("UPDATE messages SET new_message = ? WHERE uuid = ? AND room_uuid = ? AND channel_uuid = ?", (generation.aes_encrypt(new_message, hash), uuid, channels.room_of(channel_uuid), channel_uuid))
    except sqlite3.OperationalError:
        raise Exception("nomessage")
    else:
        connection.commit()
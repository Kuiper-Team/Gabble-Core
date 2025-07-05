import sqlite3
from datetime import datetime

import database.channels as channels
import utilities.generation as generation
from database.connection import connection, cursor
from utilities.uuidv7 import uuid_v7

cursor.execute("""CREATE TABLE IF NOT EXISTS messages (
body TEXT NOT NULL,
uuid TEXT NOT NULL,
username TEXT NOT NULL,
room_uuid TEXT,
channel_uuid TEXT NOT NULL,
timestamp TEXT NOT NULL,
PRIMARY KEY (uuid))
"""
)

def create(body, username, channel_uuid, public_key):
    try:
        uuid = uuid_v7().hex
        timestamp = generation.unix_timestamp(datetime.now())
        cursor.execute("INSERT INTO messages VALUES (?, ?, ?, ?, ?, ?)", (generation.rsa_encrypt(body, public_key), uuid, username, channels.room_of(channel_uuid), channel_uuid, generation.rsa_encrypt(timestamp, public_key)), public_key)
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

def edit(new_body, uuid, channel_uuid, public_key):
    try:
        cursor.execute("UPDATE messages SET body = ? WHERE uuid = ? AND room_uuid = ? AND channel_uuid = ?", (generation.aes_encrypt(new_body, public_key), uuid, channels.room_of(channel_uuid), channel_uuid))
    except sqlite3.OperationalError:
        raise Exception("nomessage")
    else:
        connection.commit()
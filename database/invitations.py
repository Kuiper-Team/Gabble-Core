import sqlite3
from sys import path

path.append("..")

import utilities.generation as generation
from database.connection import connection, cursor
from utilities.uuidv7 import uuid_v7

cursor.execute("CREATE TABLE IF NOT EXISTS invitations (message TEXT, uuid TEXT NOT NULL, room_uuid TEXT NOT NULL, type INTEGER NOT NULL, expiry INTEGER NOT NULL, PRIMARY KEY (uuid))")

def create(title, room_uuid, type, expiry, hash):
    try:
        cursor.execute("INSERT INTO invitations VALUES (?, ?, ?, ?, ?)", (generation.aes_encrypt(title, hash), uuid_v7().hex, room_uuid, type, expiry))
    except sqlite3.OperationalError:
        raise Exception("couldntinsert")
    else:
        connection.commit()

def delete(uuid):
    try:
        cursor.execute("DELETE FROM invitations WHERE uuid = ?", (uuid))
    except sqlite3.OperationalError:
        raise Exception("noinvitation")
    else:
        connection.commit()

def update_title(new_title, uuid, hash):
    try:
        cursor.execute("UPDATE invitations SET title = ? WHERE uuid = ?", (generation.aes_encrypt(new_title, hash), uuid))
    except sqlite3.OperationalError:
        raise Exception("noinvitation")
    else:
        connection.commit()
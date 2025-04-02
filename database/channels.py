import json
import sqlite3
import sys

sys.path.append("..")

import utilities.generation as generation
from database.connection import connection, cursor
from utilities.uuidv7 import uuid_v7

cursor.execute("""CREATE TABLE IF NOT EXISTS channels (
title TEXT NOT NULL,
uuid TEXT NOT NULL,
room_uuid TEXT NOT NULL,
type INTEGER NOT NULL,
settings TEXT NOT NULL,
permissions TEXT NOT NULL
PRIMARY KEY (uuid))
""")

def create(title, room_uuid, type, settings, permissions_map, public_key, administrator_hash):
    #Type 0: Text channel
    #Type 1: Voice channel
    if not 0 <= type <= 1:
        raise Exception("invalidtype")

    try:
        cursor.execute("INSERT INTO channels VALUES (?, ?, ?, ?, ?, ?)", (generation.rsa_encrypt(title, public_key), uuid_v7().hex, room_uuid, generation.rsa_encrypt(type, public_key), generation.aes_encrypt(settings, administrator_hash), generation.aes_encrypt(permissions_map, administrator_hash)))
    except sqlite3.OperationalError:
        raise Exception("channelexists")
    else:
        connection.commit()

def delete(uuid, room_uuid, public_key, private_key):
    try:
        cursor.execute("DELETE FROM channels WHERE uuid = ? AND room_uuid = ?", (uuid, room_uuid))
    except sqlite3.OperationalError:
        raise Exception("nochannel")
    else:
        connection.commit()

        try:
            try:
                channels = json.loads(generation.rsa_decrypt(cursor.execute("SELECT channels FROM rooms WHERE uuid = ?", (uuid,)), private_key))
            except sqlite3.OperationalError:
                raise Exception("noroom")

            cursor.execute("UPDATE rooms SET channels = ? WHERE uuid = ?", (generation.rsa_encrypt(json.dumps(channels.pop(uuid)), public_key), uuid))
        except sqlite3.OperationalError:
            raise Exception("noroom")

def update(uuid, settings=None, permissions_map=None):
    if settings:
        try:
            cursor.execute("UPDATE rooms SET settings = ? WHERE uuid = ?", (settings, uuid))
        except sqlite3.OperationalError:
            raise Exception("nouser")
        else:
            connection.commit()
    if permissions_map:
        try:
            cursor.execute("UPDATE rooms SET permissions_map = ? WHERE uuid = ?", (permissions_map, uuid))
        except sqlite3.OperationalError:
            raise Exception("nouser")
        else:
            connection.commit()

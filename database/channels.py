import json
import sqlite3

import utilities.generation as generation
from database.connection import connection, cursor

cursor.execute("""CREATE TABLE IF NOT EXISTS channels (
title TEXT NOT NULL,
uuid TEXT NOT NULL,
room_uuid TEXT NOT NULL,
type INTEGER NOT NULL,
settings TEXT NOT NULL,
permissions_map TEXT NOT NULL,
tags TEXT,
PRIMARY KEY (uuid))
""")

#create yok, rooms.py'a bakınız.

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

def update(uuid, settings=None, permissions_map=None, tags=None):
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
    if tags:
        try:
            cursor.execute("UPDATE rooms SET tags = ? WHERE uuid = ?", (permissions_map, uuid))
        except sqlite3.OperationalError:
            raise Exception("nouser")
        else:
            connection.commit()

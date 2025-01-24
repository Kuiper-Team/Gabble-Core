import sqlite3
from sys import path

path.append("..")

import utilities.generation as generation
from connection import connection, cursor
from utilities.uuidv7 import uuid_v7

cursor.execute("CREATE TABLE IF NOT EXISTS channels (title TEXT NOT NULL, uuid TEXT NOT NULL, group_uuid TEXT NOT NULL, type INTEGER NOT NULL, settings TEXT NOT NULL, permissions_map TEXT NOT NULL, tags TEXT, PRIMARY KEY (uuid))")

def create(title, group_uuid, type, settings, permissions_map, tags, hash):
    try:
        cursor.execute("INSERT INTO channels VALUES (?, ?, ?, ?, ?, ?, ?)", (generation.aes_encrypt(title, hash), uuid_v7().hex, group_uuid, generation.aes_encrypt(type, hash), generation.aes_encrypt(settings, hash), generation.aes_encrypt(permissions_map, hash), generation.aes_encrypt(tags, hash)))
    except sqlite3.OperationalError:
        raise Exception("channelexists")
    else:
        connection.commit()

def delete(uuid, group_uuid):
    try:
        cursor.execute("DELETE FROM channels WHERE uuid = ? AND group_uuid = ?", (uuid, group_uuid))
    except sqlite3.OperationalError:
        raise Exception("nochannel")
    else:
        connection.commit()

def apply_config(title, uuid, settings, permissions_map, tags):
    try:
        cursor.execute("UPDATE channels SET title = ?, settings = ?, permissions_map = ?, tags = ?  WHERE uuid = ?", (title, settings, permissions_map, tags, uuid))
    except sqlite3.OperationalError:
        raise Exception("nochannel")
    else:
        connection.commit()
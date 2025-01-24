import sqlite3
from sys import path

path.append("..")

import utilities.generation as generation
from connection import connection, cursor
from utilities.uuidv7 import uuid_v7

cursor.execute("CREATE TABLE IF NOT EXISTS groups (title TEXT NOT NULL, uuid TEXT NOT NULL, channels TEXT, settings TEXT NOT NULL, permissions_map TEXT NOT NULL, PRIMARY KEY (uuid))")
#"channels" formatı: kanal_türü_numarası + kanal uuid'si + virgül + ...

def create(title, group_uuid, type, settings, permissions_map, tags, hash):
    try:
        cursor.execute("INSERT INTO groups VALUES (?, ?, ?, ?, ?)", (generation.aes_encrypt(title, hash), uuid_v7().hex, None, generation.aes_encrypt(settings, hash), generation.aes_encrypt(permissions_map, hash)))
    except sqlite3.OperationalError:
        raise Exception("couldntinsert")
    else:
        connection.commit()

def delete(uuid):
    try:
        cursor.execute("DELETE FROM groups WHERE uuid = ?", (uuid,))
    except sqlite3.OperationalError:
        raise Exception("nochannel")
    else:
        connection.commit()

def add_channel(uuid, channel):
    pass #Hazır değil.

def apply_config(title, uuid, settings, permissions_map):
    try:
        cursor.execute("UPDATE groups SET title = ?, settings = ?, permissions_map = ?  WHERE uuid = ?", (title, settings, permissions_map, uuid))
    except sqlite3.OperationalError:
        raise Exception("nogroup")
    else:
        connection.commit()
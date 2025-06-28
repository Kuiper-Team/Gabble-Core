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

default_settings = {
    #
}

default_pm = {
    #
}

def create(title, room_uuid, voice_channel, public_key):
    #Type 0: Text channel
    #Type 1: Voice channel
    try:
        cursor.execute("INSERT INTO channels VALUES (?, ?, ?, ?, ?, ?)", (generation.rsa_encrypt(title, public_key), uuid_v7().hex, room_uuid, generation.rsa_encrypt("1" if voice_channel else "0", public_key), generation.rsa_encrypt(default_settings, public_key), generation.rsa_encrypt(default_pm, public_key)))
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

def update(uuid, settings=None, permissions=None):
    if settings:
        try:
            cursor.execute("UPDATE rooms SET settings = ? WHERE uuid = ?", (settings, uuid))
        except sqlite3.OperationalError:
            raise Exception("nouser")
        else:
            connection.commit()
    if permissions:
        try:
            cursor.execute("UPDATE rooms SET permissions = ? WHERE uuid = ?", (permissions, uuid))
        except sqlite3.OperationalError:
            raise Exception("nouser")
        else:
            connection.commit()

def room_of(uuid):
    try:
        room_uuid = cursor.execute("SELECT room_uuid FROM channels WHERE uuid = ?", (uuid,))
    except sqlite3.OperationalError:
        raise Exception("nochannel")
    else:
        return room_uuid
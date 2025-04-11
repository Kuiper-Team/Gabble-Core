import json
import sqlite3
import sys
from datetime import datetime

sys.path.append("..")

import utilities.generation as generation
from database.connection import connection, cursor
from utilities.uuidv7 import uuid_v7

cursor.execute("""CREATE TABLE IF NOT EXISTS rooms (
title TEXT NOT NULL,
uuid TEXT NOT NULL,
public_key TEXT NOT NULL,
channels TEXT,
members TEXT NOT NULL,
settings TEXT NOT NULL,
permissions TEXT NOT NULL
PRIMARY KEY (uuid))
""")

default_settings = json.dumps(
    {
        "icon": 0
    }
)

default_permissions = json.dumps(
    {
        "tags": {},
        "members": {}
    }
)

def create(title, username):
    key_pair = generation.rsa_generate_pair()
    public_key = key_pair[0]
    uuid = uuid_v7().hex
    try:
        cursor.execute("INSERT INTO rooms VALUES (?, ?, ?, ?, ?, ?, ?)", (generation.rsa_encrypt(title, public_key), uuid, public_key, None, generation.rsa_encrypt(username, public_key), generation.rsa_encrypt(default_settings, public_key), generation.rsa_encrypt(default_permissions, public_key)))
    except sqlite3.OperationalError:
        raise Exception("roomexists")
    else:
        connection.commit()

        return public_key, key_pair[1], uuid

def delete(uuid):
    try:
        cursor.execute("DELETE FROM rooms WHERE uuid = ?", (uuid,))
    except sqlite3.OperationalError:
        raise Exception("noroom")
    else:
        connection.commit()

def update(uuid, settings=None, permissions=None):
    if settings:
        try:
            cursor.execute("UPDATE rooms SET settings = ? WHERE uuid = ?", (settings, uuid))
        except sqlite3.OperationalError:
            raise Exception("noroom")
        else:
            connection.commit()
    if permissions:
        try:
            cursor.execute("UPDATE rooms SET permissions = ? WHERE uuid = ?", (permissions, uuid))
        except sqlite3.OperationalError:
            raise Exception("noroom")
        else:
            connection.commit()

def has_permissions(uuid, username, requested, private_key):
    try:
        permissions = json.loads(generation.rsa_decrypt(cursor.execute("SELECT permissions FROM rooms WHERE uuid = ?", (uuid,)).fetchone()[0], private_key))
    except sqlite3.OperationalError:
        return False
    else:
        result = []
        for permission in requested:
            result.append(permissions["members"][username][permission])

        return result

def channels(uuid, private_key):
    try:
        channels = generation.rsa_decrypt(cursor.execute("SELECT members FROM rooms WHERE uuid = ?", (uuid,)).fetchone()[0], private_key)
    except sqlite3.OperationalError:
        raise Exception("noroom")
    else:
        return channels.split(",") if channels is not None else []

def members(uuid, private_key):
    try:
        members = generation.rsa_decrypt(cursor.execute("SELECT members FROM rooms WHERE uuid = ?", (uuid,)).fetchone()[0], private_key)
    except sqlite3.OperationalError:
        raise Exception("noroom")
    else:
        return members.split(",")

def add_member(new_member, uuid, private_key):
    try:
        members = generation.rsa_decrypt(cursor.execute("SELECT members FROM rooms WHERE uuid = ?", (uuid,)).fetchone()[0], private_key)
    except sqlite3.OperationalError:
        raise Exception("noroom")
    else:
        if new_member in members.split(","): raise Exception("alreadyamember")

        try:
            cursor.execute("UPDATE rooms SET members = ? WHERE uuid = ?", (generation.rsa_encrypt(json.dumps(json.loads(members.update({new_member: generation.unix_timestamp(datetime.now())}))), public_key(uuid)), uuid))
        except sqlite3.OperationalError:
            raise Exception("noroom")
        else:
            connection.commit()

def kick_member(member, uuid, private_key):
    try:
        members = generation.rsa_decrypt(cursor.execute("SELECT members FROM rooms WHERE uuid = ?", (uuid,)).fetchone()[0], private_key)
    except sqlite3.OperationalError:
        raise Exception("noroom")
    else:
        if not member in members.split(","): raise Exception("nomember")

        try:
            cursor.execute("UPDATE rooms SET members = ? WHERE uuid = ?", (generation.rsa_encrypt(json.dumps(json.loads(members.pop(member))), public_key(uuid)), uuid))
        except sqlite3.OperationalError:
            raise Exception("noroom")
        else:
            connection.commit()

def public_key(uuid):
    try:
        key = cursor.execute("SELECT public_key FROM rooms WHERE uuid = ?", (uuid,)).fetchone()[0]
    except sqlite3.OperationalError:
        raise Exception("noroom")
    else:
        return key
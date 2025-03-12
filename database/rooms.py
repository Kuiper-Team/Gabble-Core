import json
import sqlite3
from datetime import datetime

import utilities.generation as generation
from config import room
from database.connection import connection, cursor
from utilities.uuidv7 import uuid_v7

cursor.execute("""CREATE TABLE IF NOT EXISTS rooms (
title TEXT NOT NULL,
uuid TEXT NOT NULL,
public_key TEXT NOT NULL,
channels TEXT,
members TEXT NOT NULL,
settings TEXT NOT NULL,
permissions_map TEXT NOT NULL
PRIMARY KEY (uuid))
""")
#"permissions_map" formatı:
#   "tags": {
#       "Şah": {
#       "icon": "(dosya uuidsi...)",
#       "color": "17CA4D",
#       "permissions": { (yetki haritası...) }
#   }
#}
#   "members": {
#       "Faysal": {
#           "icon": "(dosya uuidsi...)",
#          "color": "17CA4D",
#          "permissions": { (yetki haritası...) }
#      }
#   }

def create(title, username):
    key_pair = generation.rsa_generate_pair(),
    public_key = key_pair[0]
    administrator_hash = generation.random_sha256_hash()
    try:
        cursor.execute("INSERT INTO rooms VALUES (?, ?, ?, ?, ?, ?, ?)", (generation.rsa_encrypt(title, public_key), uuid_v7().hex, public_key, None, generation.rsa_encrypt(username, public_key), generation.aes_encrypt(room.default_settings_0 if type == 0 else room.default_settings_1, administrator_hash), generation.aes_encrypt(room.default_pm.format(username), administrator_hash)))
    except sqlite3.OperationalError:
        raise Exception("roomexists")
    else:
        connection.commit()

        return public_key, key_pair[1], administrator_hash

def delete(uuid):
    try:
        cursor.execute("DELETE FROM rooms WHERE uuid = ?", (uuid,))
    except sqlite3.OperationalError:
        raise Exception("noroom")
    else:
        connection.commit()

def create_channel(title, room_uuid, type, settings, permissions_map, tags, public_key, administrator_hash):
    if not 0 <= type <= 1:
        raise Exception("invalidtype")

    try:
        cursor.execute("INSERT INTO channels VALUES (?, ?, ?, ?, ?, ?, ?)", (generation.rsa_encrypt(title, public_key), uuid_v7().hex, room_uuid, generation.rsa_encrypt(type, public_key), generation.aes_encrypt(settings, administrator_hash), generation.aes_encrypt(permissions_map, administrator_hash), None))
    except sqlite3.OperationalError:
        raise Exception("channelexists")
    else:
        connection.commit()

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

def members(uuid, private_key):
    try:
        members = generation.rsa_decrypt(cursor.execute("SELECT members FROM rooms WHERE uuid = ?", (uuid,)).fetchone()[0], private_key)
    except sqlite3.OperationalError:
        raise Exception("noroom")
    else:
        return members.split(",")

def has_permissions(uuid, username, permissions, administrator_hash):
    try:
        pm = json.loads(generation.aes_decrypt(cursor.execute("SELECT permissions_map FROM rooms WHERE uuid = ?", (uuid,)).fetchone()[0], administrator_hash))
    except sqlite3.OperationalError:
        return False
    else:
        for permission in permissions:
            if pm["members"][username][permission]:
                continue
            else:
                return False

        return True

def add_member(new_member, uuid, public_key, private_key):
    try:
        members = json.loads(generation.rsa_decrypt(cursor.execute("SELECT members FROM rooms WHERE uuid = ?", (uuid,)).fetchone()[0], private_key))
    except sqlite3.OperationalError:
        raise Exception("noroom")
    else:
        try:
            cursor.execute("UPDATE rooms SET members = ? WHERE uuid = ?", (generation.rsa_encrypt(json.dumps(json.loads(members.update({new_member: generation.unix_timestamp(datetime.now())}))), public_key), uuid))
        except sqlite3.OperationalError:
            raise Exception("noroom")
        else:
            connection.commit()

def kick_member(member, uuid, public_key, private_key): #Eğer öyle bir üye listede yoksa API erkenden hata mesajı göndermeli.
    try:
        members = json.loads(generation.rsa_decrypt(cursor.execute("SELECT members FROM rooms WHERE uuid = ?", (uuid,)).fetchone()[0], private_key))
    except sqlite3.OperationalError:
        raise Exception("noroom")
    else:
        try:
            cursor.execute("UPDATE rooms SET members = ? WHERE uuid = ?", (generation.rsa_encrypt(json.dumps(json.loads(members.pop(member))), public_key), uuid))
        except sqlite3.OperationalError:
            raise Exception("noroom")
        else:
            connection.commit()

def public_key(uuid):
    try:
        public_key = cursor.execute("SELECT public_key FROM rooms WHERE uuid = ?", (uuid,)).fetchone()[0]
    except sqlite3.OperationalError:
        raise Exception("noroom")
    else:
        return public_key
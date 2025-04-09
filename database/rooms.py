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
settings TEXT,
permissions TEXT NOT NULL,
administrator_hash TEXT NOT NULL,
PRIMARY KEY (uuid))
""")
#"permissions_map" formatı:
#   "tags": {
#       "Şah": {
#       "color": "17CA4D",
#       "permissions": { (yetki haritası...) }
#   }
#}
#   "members": {
#       "Faysal": {
#          "color": "17CA4D",
#          "permissions": { (yetki haritası...) }
#      }
#   }

default_permissions = json.dumps(
    {
        "tags": {},
        "members": {}
    }
)

def create(title, username):
    key_pair = generation.rsa_generate_pair()
    public_key = key_pair[0]
    administrator_hash = generation.random_sha256_hash()
    uuid = uuid_v7().hex
    try:
        cursor.execute("INSERT INTO rooms VALUES (?, ?, ?, ?, ?, ?, ?)", (generation.rsa_encrypt(title, public_key), uuid, public_key, None, generation.rsa_encrypt(username, public_key), None, generation.aes_encrypt(default_permissions, administrator_hash), administrator_hash))
    except sqlite3.OperationalError:
        raise Exception("roomexists")
    else:
        connection.commit()

        return public_key, key_pair[1], administrator_hash, uuid

def delete(uuid):
    try:
        cursor.execute("DELETE FROM rooms WHERE uuid = ?", (uuid,))
    except sqlite3.OperationalError:
        raise Exception("noroom")
    else:
        connection.commit()

def update(uuid, settings=None):
    if settings:
        try:
            cursor.execute("UPDATE rooms SET settings = ? WHERE uuid = ?", (settings, uuid))
        except sqlite3.OperationalError:
            raise Exception("noroom")
        else:
            connection.commit()

def has_permissions(uuid, username, requested, administrator_hash):
    try:
        permissions = json.loads(generation.aes_decrypt(cursor.execute("SELECT permissions FROM rooms WHERE uuid = ?", (uuid,)).fetchone()[0], administrator_hash))
    except sqlite3.OperationalError:
        return False
    else:
        result = []
        for permission in requested:
            result.append(permissions["members"][username][permission])

        return result

#Permissions will be decided later.
def update_permissions_tag(uuid, administrator_hash, title, color=None,
    view_channels=None
): #Both for creation and updating...
    try:
        current_permissions = generation.aes_decrypt(cursor.execute("SELECT permissions FROM rooms WHERE uuid = ?", (uuid,)).fetchone()[0], administrator_hash)
    except sqlite3.OperationalError:
        raise Exception("noroom")
    else:
        modified_permissions = current_permissions
        modified_permissions["tag"][title] = {}
        modified_permissions["tag"][title]["color"] = color
        modified_permissions["tag"][title]["permissions"] = {}

        if view_channels: modified_permissions["tag"][title]["permissions"]["view_channels"] = view_channels
        try:
            cursor.execute("UPDATE rooms SET permissions = ? WHERE uuid = ?", (generation.aes_encrypt(modified_permissions, administrator_hash), uuid))
        except sqlite3.OperationalError:
            raise Exception("noroom")
        else:
            connection.commit()

def update_permissions_member(uuid, administrator_hash, color=None,
    view_channels=None
): #Both for creation and updating...
    pass #(...)

def members(uuid, private_key):
    try:
        members = generation.rsa_decrypt(cursor.execute("SELECT members FROM rooms WHERE uuid = ?", (uuid,)).fetchone()[0], private_key)
    except sqlite3.OperationalError:
        raise Exception("noroom")
    else:
        return members.split(",")

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
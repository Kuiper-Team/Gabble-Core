import sqlite3
from sys import path

path.append("..")

import utilities.generation as generation
from connection import connection, cursor
from utilities.uuidv7 import uuid_v7

cursor.execute("CREATE TABLE IF NOT EXISTS rooms (title TEXT NOT NULL, uuid TEXT NOT NULL, channels TEXT, members TEXT NOT NULL, settings TEXT NOT NULL, permissions_map TEXT NOT NULL, PRIMARY KEY (uuid))")
#"channels" formatı: kanal_türü_numarası + kanal uuid'si + yıldız + ...
#"members" formatı: kullanıcı_adı_1*kullanıcı_adı_2*...
#"permissions_map" formatı:
#"tags": {
#   "Şah": {
#       "icon": "(dosya uuidsi...)",
#       "color": 0x17CA4D,
#       "permissions_map": { (yetki haritası...) }
#   }
#}
#"members": {
#   "Faysal": {
#       "icon": "(dosya uuidsi...)",
#       "color": 0x17CA4D,
#       "permission_map": { (yetki haritası...) }
#   }
#}

def create(title, settings, permissions_map, username, hash):
    try:
        cursor.execute("INSERT INTO rooms VALUES (?, ?, ?, ?, ?, ?)", (generation.aes_encrypt(title, hash), uuid_v7().hex, None, generation.aes_encrypt(username, hash), generation.aes_encrypt(settings, hash), generation.aes_encrypt(permissions_map, hash)))
    except sqlite3.OperationalError:
        raise Exception("roomexists")
    else:
        connection.commit()

def delete(uuid):
    try:
        cursor.execute("DELETE FROM rooms WHERE uuid = ?", (uuid,))
    except sqlite3.OperationalError:
        raise Exception("noroom")
    else:
        connection.commit()

def create_channel(title, room_uuid, type, settings, permissions_map, tags, hash):
    try:
        cursor.execute("INSERT INTO channels VALUES (?, ?, ?, ?, ?, ?, ?)", (generation.aes_encrypt(title, hash), uuid_v7().hex, room_uuid, generation.aes_encrypt(type, hash), generation.aes_encrypt(settings, hash), generation.aes_encrypt(permissions_map, hash), generation.aes_encrypt(tags, hash)))
    except sqlite3.OperationalError:
        raise Exception("channelexists")
    else:
        connection.commit()

def apply_config(title, uuid, settings, permissions_map):
    try:
        cursor.execute("UPDATE rooms SET title = ?, settings = ?, permissions_map = ?  WHERE uuid = ?", (title, settings, permissions_map, uuid))
    except sqlite3.OperationalError:
        raise Exception("noroom")
    else:
        connection.commit()

def add_member(new_member, uuid, hash):
    members = None
    try:
        members = generation.aes_decrypt(cursor.execute("SELECT members FROM rooms WHERE uuid = ?", (uuid,)).fetchone()[0], hash)
    except sqlite3.OperationalError:
        raise Exception("noroom")
    else:
        try:
            cursor.execute("UPDATE rooms SET members = ? WHERE uuid = ?", (members + "*" + new_member, uuid))
        except sqlite3.OperationalError:
            raise Exception("couldntupdate")
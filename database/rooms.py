#SUNUCUNUN KURUCUSUNUN HASH'İ İLE ŞİFRELENİYOR.
import json
import sqlite3
from sys import path

path.append("..")

import utilities.generation as generation
from config import room
from database.connection import connection, cursor
from utilities.uuidv7 import uuid_v7

cursor.execute("CREATE TABLE IF NOT EXISTS rooms (title TEXT NOT NULL, uuid TEXT NOT NULL, type INTEGER NOT NULL, channels TEXT, owner TEXT NOT NULL, members TEXT, settings TEXT NOT NULL, permissions_map TEXT NOT NULL, PRIMARY KEY (uuid))")
#"channels" formatı: kanal_türü_numarası + kanal uuid'si + yıldız + ...
#"members" formatı: kullanıcı_adı_1,kullanıcı_adı_2,...
#"permissions_map" formatı:
#"tags": {
#   "Şah": {
#       "icon": "(dosya uuidsi...)",
#       "color": "17CA4D",
#       "permissions": { (yetki haritası...) }
#   }
#}
#"members": {
#   "Faysal": {
#       "icon": "(dosya uuidsi...)",
#       "color": "17CA4D",
#       "permissions": { (yetki haritası...) }
#   }
#}

#type (room) için
#0: Topluluk odası
#1: Direkt mesajlaşma odası
def create(title, type, username, hash):
    if not 0 <= type <= 1:
        raise Exception("invalidtype")

    try:
        cursor.execute("INSERT INTO rooms VALUES (?, ?, ?, ?, ?, ?, ?)", (generation.aes_encrypt(title, hash), uuid_v7().hex, type, None, username, None, generation.aes_encrypt(room.default_settings_0 if type == 0 else room.default_settings_1, hash), generation.aes_encrypt(room.default_pm.format(username), hash)))
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

#type (channel) için
#0: Metin kanalı
#1: Ses kanalı
def create_channel(title, room_uuid, type, settings, permissions_map, tags, hash):
    if not 0 <= type <= 1:
        raise Exception("invalidtype")

    try:
        cursor.execute("INSERT INTO channels VALUES (?, ?, ?, ?, ?, ?, ?)", (generation.aes_encrypt(title, hash), uuid_v7().hex, room_uuid, generation.aes_encrypt(type, hash), generation.aes_encrypt(settings, hash), generation.aes_encrypt(permissions_map, hash), generation.aes_encrypt(tags, hash)))
    except sqlite3.OperationalError:
        raise Exception("channelexists")
    else:
        connection.commit()

def apply_config(title, uuid, settings, permissions_map, hash):
    try:
        cursor.execute("UPDATE rooms SET title = ?, settings = ?, permissions_map = ?  WHERE uuid = ?", (title, generation.aes_encrypt(settings, hash), generation.aes_encrypt(permissions_map, hash), uuid))
    except sqlite3.OperationalError:
        raise Exception("noroom")
    else:
        connection.commit()

def members(uuid, hash):
    members = None
    try:
        members = generation.aes_decrypt(cursor.execute("SELECT members FROM rooms WHERE uuid = ?", (uuid,)).fetchone()[0], hash)
    except sqlite3.OperationalError:
        raise Exception("noroom")
    else:
        return members.split(",")

def owner(uuid):
    owner = None
    try:
        owner = cursor.execute("SELECT owner FROM rooms WHERE uuid = ?", (uuid,)).fetchone()[0]
    except sqlite3.OperationalError:
        raise Exception("noroom")
    else:
        return owner

def has_permissions(uuid, username, permissions, hash):
    has_permission = None
    try:
        pm = json.loads(generation.aes_decrypt(cursor.execute("SELECT permissions_map FROM rooms WHERE uuid = ?", (uuid,)).fetchone()[0], hash))
    except sqlite3.OperationalError:
        return False
    else:
        for permission in permissions:
            if pm["members"][username][permission]:
                continue
            else:
                return False

        return True

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
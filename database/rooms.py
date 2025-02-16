import json
import sqlite3

import utilities.generation as generation
from config import room
from database.connection import connection, cursor
from utilities.uuidv7 import uuid_v7

cursor.execute("CREATE TABLE IF NOT EXISTS rooms (title TEXT NOT NULL, uuid TEXT NOT NULL, public_key TEXT NOT NULL, type INTEGER NOT NULL, channels TEXT, members TEXT NOT NULL, settings TEXT NOT NULL, permissions_map TEXT NOT NULL, PRIMARY KEY (uuid))")
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

#type için,
#0: Direkt mesajlaşma odası (iki kişilik)
#1: Sohbet odası
def create(title, type, username):
    key_pair = generation.rsa_generate_pair(),
    public_key = key_pair[0]

    if type == 0: #Hepsine RSA
        try:
            cursor.execute("INSERT INTO rooms VALUES (?, ?, ?, ?, ?, ?, ?)", (generation.rsa_encrypt(title, public_key), uuid_v7().hex, public_key, type, None, generation.rsa_encrypt(username, public_key), generation.rsa_encrypt(room.default_settings_0 if type == 0 else room.default_settings_1, public_key), generation.rsa_encrypt(room.default_pm.format(username), public_key)))
        except sqlite3.OperationalError:
            raise Exception("roomexists")
        else:
            connection.commit()

        return public_key, key_pair
    elif type == 1: #Hassas olmayan verilere RSA, hassas olanlara AES
        administrator_hash = generation.random_sha256_hash()
        try:
            cursor.execute("INSERT INTO rooms VALUES (?, ?, ?, ?, ?, ?, ?)", (generation.rsa_encrypt(title, public_key), uuid_v7().hex, public_key, type, None, generation.rsa_encrypt(username, public_key), generation.aes_encrypt(room.default_settings_0 if type == 0 else room.default_settings_1, administrator_hash), generation.aes_encrypt(room.default_pm.format(username), administrator_hash)))
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
        cursor.execute("INSERT INTO channels VALUES (?, ?, ?, ?, ?, ?, ?)", (generation.rsa_encrypt(title, public_key), uuid_v7().hex, room_uuid, generation.rsa_encrypt(type, public_key), generation.aes_encrypt(settings, public_key), generation.aes_encrypt(permissions_map, administrator_hash), generation.aes_encrypt(tags, administrator_hash)))
    except sqlite3.OperationalError:
        raise Exception("channelexists")
    else:
        connection.commit()

def update_title(title, uuid, public_key):
    try:
        cursor.execute("UPDATE rooms SET title = ? WHERE uuid = ?", (generation.rsa_encrypt(title, public_key), uuid))
    except sqlite3.OperationalError:
        raise Exception("noroom")
    else:
        connection.commit()

def update_config(uuid, settings, permission_map, administrator_hash):
    try:
        cursor.execute("UPDATE rooms SET settings = ?, permissions_map = ? WHERE uuid = ?", (generation.aes_encrypt(settings, administrator_hash), generation.aes_encrypt(permission_map, administrator_hash)))
    except sqlite3.OperationalError:
        raise Exception("noroom")
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
    has_permission = None
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

def add_member(new_member, uuid, hash): #type 0 ise üye eklenmesine izin verilmeyecektir.
        try:
            members = generation.rsa_decrypt(cursor.execute("SELECT members FROM rooms WHERE uuid = ?", (uuid,)).fetchone()[0], hash)
        except sqlite3.OperationalError:
            raise Exception("noroom")
        else:
            try:
                cursor.execute("UPDATE rooms SET members = ? WHERE uuid = ?", (members + "*" + new_member, uuid))
            except sqlite3.OperationalError:
                raise Exception("couldntupdate")
#İstekler client tarafından nasıl taranacak?

import sqlite3
import pyargon2

import database.rooms as rooms
import database.users as users
import utilities.generation as generation
from database.connection import connection, cursor
from uuid import uuid4

cursor.execute("""CREATE TABLE IF NOT EXISTS requests (
uuid TEXT NOT NULL,
requester TEXT NOT NULL,
expiry INTEGER NOT NULL,
result TEXT NOT NULL,
PRIMARY KEY (uuid))
""")

def create(requester, expiry, result, passcode):
    try:
        request_hash = cursor.execute("SELECT request_hash FROM users WHERE username = ?", (requester,)).fetchone()[0]
    except sqlite3.OperationalError:
        raise Exception("nouser")
    else:
        connection.commit()

        hash = pyargon2.hash(request_hash, passcode)
        try:
            cursor.execute("INSERT INTO requests VALUES (?, ?, ?, ?)", (uuid4().hex, requester, generation.aes_encrypt(expiry, hash), generation.aes_encrypt(result, hash)))
        except sqlite3.OperationalError:
            raise Exception("couldntinsert")

    return hash

def withdraw(uuid):
    try:
        cursor.execute("DELETE FROM requests WHERE uuid = ?", (uuid,))
    except sqlite3.OperationalError:
        raise Exception("norequest")
    else:
        connection.commit()

#type için kodlar:
#f: Arkadaşlık isteği
#i: Oda daveti
def accept(uuid, passcode, room_private_key = None):
    try:
        requester = cursor.execute("SELECT requester FROM requests WHERE uuid = ?", (uuid,)).fetchone()[0]
        result = generation.aes_decrypt(cursor.execute("SELECT result FROM requests WHERE uuid = ?", (uuid,)).fetchone()[0], pyargon2.hash(cursor.execute("SELECT request_hash FROM users WHERE username = ?", (requester,)).fetchone()[0], passcode)).split(",")
    except sqlite3.OperationalError:
        raise Exception("norequest")
    else:
        if result[0] == "f": #f,username1,username2
            users.add_friends(result[1], result[2])
        elif result[0] == "i" and room_private_key: #i,uuid,username
            rooms.add_member(result[2], result[1], room_private_key)
        else:
            raise Exception("invalidrequest")

        withdraw(uuid)
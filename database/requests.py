import sqlite3

import pyargon2
from sys import path

from utilities.generation import aes_encrypt

path.append("..")

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
            cursor.execute("INSERT INTO requests VALUES (?, ?, ?, ?)", (uuid4().hex, requester, aes_encrypt(expiry, hash), aes_encrypt(result, hash)))
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
#Her gün tarihi geçmiş süreli anahtarları temizleyen bir sistem yapılacak.
import sqlite3
from sys import path
from uuid import uuid4

path.append("..")

import utilities.generation as generation
from connection import connection, cursor

cursor.execute("CREATE TABLE IF NOT EXISTS timed_keys (uuid TEXT NOT NULL, expiration INTEGER NOT NULL, hash TEXT NOT NULL, PRIMARY KEY (uuid))")

def create_timed_key(username, password, expiration): #Oturum açmayı sağlayan fonksiyon.
    hash = None
    try:
        hash = cursor.execute("SELECT hash FROM users WHERE username = ?", (username,)).fetchone()[0]

        if generation.hashed_password(password) != hash:
            raise Exception("incorrectpassword")
    except sqlite3.OperationalError:
        raise Exception("nouser")

    try:
        uuid = None
        while uuid == cursor.execute("SELECT hash FROM users WHERE username = ?", (username,)).fetchone()[0]:
            uuid = uuid4().hex

        cursor.execute("INSERT INTO timed_keys VALUES (?, ?, ?)", (uuid, expiration, hash))
    except sqlite3.IntegrityError:
        raise Exception("failedinsert")
    else:
        connection.commit()
import sqlite3
from datetime import datetime
from sys import path

path.append("..")

import utilities.generation as generation
from config import database
from connection import connection, cursor

cursor.execute("CREATE TABLE IF NOT EXISTS users (username TEXT NOT NULL, toc INTEGER NOT NULL, hash TEXT NOT NULL, settings TEXT NOT NULL, friends TEXT, PRIMARY KEY (username))") #"friends" ve "settings", "hash" anahtarı kullanılarak AES ile oluşturulan bir şifredir.
#"hash" ve "settings" birer hash ve "settings", "hash" kullanılarak oluşturulmuş bir hashtır.

def create_user(username, password): #profile.db de katılacak.
    hash = generation.hashed_password(password)
    try:
        cursor.execute("INSERT INTO users VALUES (?, ?, ?, ?, ?)", (username, generation.unix_timestamp(datetime.now()), hash, ))
    except sqlite3.IntegrityError:
        raise Exception("userexists")
    else:
        connection.commit()

def delete_user(username):
    try:
        cursor.execute("DELETE FROM users WHERE username=?", (username,))
    except sqlite3.IntegrityError:
        raise Exception("nouser")
    else:
        connection.commit()
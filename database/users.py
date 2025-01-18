import sqlite3
from datetime import datetime
from sys import path

path.append("..")

import utilities.generation as generation
from config import database
from connection import connection, cursor

cursor.execute("CREATE TABLE IF NOT EXISTS users (username TEXT NOT NULL, toc INTEGER NOT NULL, hash TEXT NOT NULL, settings TEXT NOT NULL, PRIMARY KEY (username))")
#"hash" ve "settings" birer hash ve "settings", "hash" kullanılarak oluşturulmuş bir hashtır.

def create_user(username, password): #profile.db de katılacak.
    try:
        cursor.execute("INSERT INTO users VALUES (?, ?, ?, ?)", (username, generation.unix_timestamp(datetime.now()), generation.hashed_password(password), database.default_user_settings))
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
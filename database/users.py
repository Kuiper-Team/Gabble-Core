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
        cursor.execute("INSERT INTO users VALUES (?, ?, ?, ?, ?)", (username, generation.unix_timestamp(datetime.now()), hash, database.default_settings, None))
    except sqlite3.OperationalError:
        raise Exception("userexists")
    else:
        connection.commit()

def delete_user(username):
    try:
        cursor.execute("DELETE FROM users WHERE username = ?", (username,))
    except sqlite3.OperationalError:
        raise Exception("nouser")
    else:
        connection.commit()

def add_friends(username_1, username_2, hash_1, hash_2):
    encrypted_1, encrypted_2 = (None,) * 2
    try:
        encrypted_1 = cursor.execute("SELECT friends FROM users WHERE username = ?", (username_1,)).fetchone()[0]
        encrypted_2 = cursor.execute("SELECT friends FROM users WHERE username = ?", (username_2,)).fetchone()[0]

        friends_1 = generation.sha_aes_decrypt(encrypted_1, hash_1[16:], hash_1[:16])
        friends_2 = generation.sha_aes_decrypt(encrypted_2, hash_2[16:], hash_2[:16])
    except sqlite3.OperationalError:
        raise Exception("nouser")

    try:
        new_encrypted_1 = generation.sha_aes_encrypt(friends_1 + "," + username_2, hash_1[16:], hash_1[:16])
        new_encrypted_2 = generation.sha_aes_encrypt(friends_2 + "," + username_1, hash_2[16:], hash_2[:16])
        cursor.execute("INSERT INTO users (friends) VALUES(?) WHERE username = ?", (new_encrypted_1, username_1))
        cursor.execute("INSERT INTO users (friends) VALUES(?) WHERE username = ?", (new_encrypted_2, username_2))
    except sqlite3.OperationalError:
        raise Exception("couldntinsert")
    else:
        connection.commit()

def apply_settings(username, settings):
    pass #EĞER KULLANICI VARSA settings sütununu düzenleyecek.
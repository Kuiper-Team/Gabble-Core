import json
import sqlite3
from hashlib import sha256
from sys import path

path.append("..")

import utilities.generation as generation
from config import database
from database.connection import connection, cursor

cursor.execute("""CREATE TABLE IF NOT EXISTS users (
username TEXT NOT NULL,
display_name TEXT,
settings TEXT NOT NULL,
room_settings TEXT,
channel_settings TEXT,
friends TEXT,
biography TEXT,
request_hash TEXT NOT NULL,
key_chain TEXT NOT NULL,
PRIMARY KEY (username))
""")

def create(username, password):
    hash = generation.hashed_password(password)
    try:
        cursor.execute("INSERT INTO users VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", (username, username, generation.aes_encrypt(database.default_user_settings, hash), None, None, None, None, sha256(username.encode("utf-8")).hexdigest(), generation.aes_encrypt("{}", hash)))
    except sqlite3.OperationalError:
        raise Exception("userexists")
    else:
        connection.commit()

        return hash

def delete(username):
    try:
        cursor.execute("DELETE FROM users WHERE username = ?", (username,))
    except sqlite3.OperationalError:
        raise Exception("nouser")
    else:
        connection.commit()

def add_friends(username_1, username_2, hash_1, hash_2):
    try:
        encrypted_1 = cursor.execute("SELECT friends FROM users WHERE username = ?", (username_1,)).fetchone()[0]
        encrypted_2 = cursor.execute("SELECT friends FROM users WHERE username = ?", (username_2,)).fetchone()[0]

        friends_1 = generation.aes_decrypt(encrypted_1, hash_1)
        friends_2 = generation.aes_decrypt(encrypted_2, hash_2)
    except sqlite3.OperationalError:
        raise Exception("nouser")
    else:
        try:
            new_encrypted_1 = generation.aes_encrypt(friends_1 + "," + username_2, hash_1)
            new_encrypted_2 = generation.aes_encrypt(friends_2 + "," + username_1, hash_2)
            cursor.execute("INSERT OR REPLACE INTO users (friends) VALUES(?) WHERE username = ?", (new_encrypted_1, username_1))
            cursor.execute("INSERT OR REPLACE INTO users (friends) VALUES(?) WHERE username = ?", (new_encrypted_2, username_2))
        except sqlite3.OperationalError:
            raise Exception("couldntinsert")
        else:
            connection.commit()

def update(): #Hazırlanacak.
    pass

def exists(username):
    try:
        cursor.execute("SELECT username FROM users WHERE username = ?", (username,))
    except sqlite3.OperationalError:
        return False
    else:
        return True

def verify_hash(username, hash):
    try:
        return hash == cursor.execute("SELECT hash FROM users WHERE username = ?", (username,)).fetchone()[0]
    except sqlite3.OperationalError:
        return False

def check_credentials(username, password):
    try:
        return generation.hashed_password(password) == cursor.execute("SELECT hash FROM users WHERE username = ?", (username,)).fetchone()[0]
    except sqlite3.OperationalError:
        return False

def key_chain(username, hash):
    try:
       dictionary = generation.aes_decrypt(cursor.execute("SELECT key_chain FROM users WHERE username = ?", (username,)).fetchone()[0], hash)
    except sqlite3.OperationalError:
        raise Exception("nouser")
    else:
        return json.loads(dictionary)

def append_to_key_chain(username, hash, label, key):
    try:
        dictionary = key_chain(username, hash)
    except Exception as code:
        raise Exception(code)
    else:
        json_data = json.dumps(dictionary.update({label: key}))
        cursor.execute("UPDATE users SET key_chain = ? WHERE username = ?", (json_data, username))
        cursor.commit()

def delete_from_key_chain(username, hash, label):
    try:
        dictionary = key_chain(username, hash)
    except Exception as code:
        raise Exception(code)
    else:
        json_data = json.dumps(dictionary.pop(label))
        cursor.execute("UPDATE users SET key_chain = ? WHERE username = ?", (json_data, username))
        cursor.commit()
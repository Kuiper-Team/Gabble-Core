import json
import sqlite3
import sys
from Crypto.Random import get_random_bytes
from hashlib import sha256

sys.path.append("..")

import utilities.generation as generation
from database.connection import connection, cursor

cursor.execute("""CREATE TABLE IF NOT EXISTS users (
username TEXT NOT NULL,
display_name TEXT,
settings TEXT NOT NULL,
room_settings TEXT NOT NULL,
channel_settings TEXT NOT NULL,
friends TEXT,
biography TEXT,
request_hash TEXT NOT NULL,
inbox TEXT NOT NULL,
key_chain TEXT NOT NULL,
PRIMARY KEY (username))
""")

default_settings = json.dump(
    {
        "icon": 0
    }
)

default_room_settings = json.dumps(
    {

    }
)

default_channel_settings = json.dumps(
    {

    }
)

def create(username, password):
    salt = get_random_bytes(16)
    hash = generation.hashed_password(password, salt)
    try:
        cursor.execute("INSERT INTO user VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (username, username, None, default_settings, default_room_settings, default_channel_settings, None, sha256(username.encode("utf-8")).hexdigest(), generation.aes_encrypt("{}", hash), generation.aes_encrypt("{}", hash)))
    except sqlite3.OperationalError:
        raise Exception("userexists")
    else:
        connection.commit()

        return hash, salt

def delete(username, hash):
    try:
        cursor.execute("DELETE FROM user WHERE username = ?", (username,))
    except sqlite3.OperationalError:
        raise Exception("nouser")
    else:
        connection.commit()

    #key_chain kullanılarak üye olunan odalardan da silinecek.

def add_friends(username_1, username_2, hash_1, hash_2):
    try:
        encrypted_1 = cursor.execute("SELECT friends FROM user WHERE username = ?", (username_1,)).fetchone()[0]
        encrypted_2 = cursor.execute("SELECT friends FROM user WHERE username = ?", (username_2,)).fetchone()[0]

        friends_1 = generation.aes_decrypt(encrypted_1, hash_1)
        friends_2 = generation.aes_decrypt(encrypted_2, hash_2)
    except sqlite3.OperationalError:
        raise Exception("nouser")
    else:
        try:
            new_encrypted_1 = generation.aes_encrypt(friends_1 + "," + username_2, hash_1)
            new_encrypted_2 = generation.aes_encrypt(friends_2 + "," + username_1, hash_2)
            cursor.execute("INSERT OR REPLACE INTO user (friends) VALUES(?) WHERE username = ?", (new_encrypted_1, username_1))
            cursor.execute("INSERT OR REPLACE INTO user (friends) VALUES(?) WHERE username = ?", (new_encrypted_2, username_2))
        except sqlite3.OperationalError:
            raise Exception("couldntinsert")
        else:
            connection.commit()

def update(username, display_name=None, settings=None, room_settings=None, channel_settings=None, biography=None):
    if display_name:
        try:
            cursor.execute("UPDATE user SET display_name = ? WHERE username = ?", (display_name, username))
        except sqlite3.OperationalError:
            raise Exception("nouser")
        else:
            connection.commit()
    if settings:
        try:
            cursor.execute("UPDATE user SET settings = ? WHERE username = ?", (settings, username))
        except sqlite3.OperationalError:
            raise Exception("nouser")
        else:
            connection.commit()
    if room_settings:
        try:
            cursor.execute("UPDATE user SET room_settings = ? WHERE username = ?", (room_settings, username))
        except sqlite3.OperationalError:
            raise Exception("nouser")
        else:
            connection.commit()
    if channel_settings:
        try:
            cursor.execute("UPDATE user SET channel_settings = ? WHERE username = ?", (channel_settings, username))
        except sqlite3.OperationalError:
            raise Exception("nouser")
        else:
            connection.commit()
    if biography:
        try:
            cursor.execute("UPDATE user SET channel_settings = ? WHERE username = ?", (biography, username))
        except sqlite3.OperationalError:
            raise Exception("nouser")
        else:
            connection.commit()

def exists(username):
    try:
        cursor.execute("SELECT username FROM user WHERE username = ?", (username,))
    except sqlite3.OperationalError:
        return False
    else:
        return True

def verify_hash(username, hash):
    try:
        return hash == cursor.execute("SELECT hash FROM user WHERE username = ?", (username,)).fetchone()[0]
    except sqlite3.OperationalError:
        return False

def check_credentials(username, password):
    try:
        return generation.hashed_password(password) == cursor.execute("SELECT hash FROM user WHERE username = ?", (username,)).fetchone()[0]
    except sqlite3.OperationalError:
        return False

def key_chain(username, hash):
    try:
       dictionary = generation.aes_decrypt(cursor.execute("SELECT key_chain FROM user WHERE username = ?", (username,)).fetchone()[0], hash)
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
        cursor.execute("UPDATE user SET key_chain = ? WHERE username = ?", (json_data, username))

        connection.commit()

def delete_from_key_chain(username, hash, label):
    try:
        dictionary = key_chain(username, hash)
    except Exception as code:
        raise Exception(code)
    else:
        json_data = json.dumps(dictionary.pop(label))
        cursor.execute("UPDATE user SET key_chain = ? WHERE username = ?", (json_data, username))

        connection.commit()

def inbox(username, hash):
    try:
       dictionary = generation.aes_decrypt(cursor.execute("SELECT inbox FROM user WHERE username = ?", (username,)).fetchone()[0], hash)
    except sqlite3.OperationalError:
        raise Exception("nouser")
    else:
        return json.loads(dictionary)

def append_to_inbox(username, hash, label, key):
    try:
        dictionary = key_chain(username, hash)
    except Exception as code:
        raise Exception(code)
    else:
        json_data = json.dumps(dictionary.update({label: key}))
        cursor.execute("UPDATE user SET inbox = ? WHERE username = ?", (json_data, username))

        connection.commit()

def delete_from_inbox(username, hash, label):
    try:
        dictionary = key_chain(username, hash)
    except Exception as code:
        raise Exception(code)
    else:
        json_data = json.dumps(dictionary.pop(label))
        cursor.execute("UPDATE user SET inbox = ? WHERE username = ?", (json_data, username))

        connection.commit()
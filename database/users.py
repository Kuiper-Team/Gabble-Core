import sqlite3
from datetime import datetime
from sys import path

path.append("..")

import utilities.generation as generation
from config import database
from database.connection import connection, cursor

cursor.execute("""CREATE TABLE IF NOT EXISTS users (
username TEXT NOT NULL,
display_name TEXT,
toc INTEGER NOT NULL,
hash TEXT NOT NULL,
settings TEXT NOT NULL,
room_settings TEXT,
channel_settings TEXT,
friends TEXT,
biography TEXT,
key_chain BLOB,
PRIMARY KEY (username))
""")

def create(username, password):
    hash = generation.hashed_password(password)
    try:
        cursor.execute("INSERT INTO users VALUES (?, ?, ?, ?, ?)", (username, generation.unix_timestamp(datetime.now()), hash, generation.aes_encrypt(database.default_user_settings, hash), None, None, None))
        cursor.execute("INSERT INTO profiles VALUES (?, ?, ?)", (username, None, 0))
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

def update(username, hash, biography=False, channel_settings=False, display_name=False, room_settings=False, settings=False):
    try:
        command = "UPDATE profiles SET " #WHERE username = ?
        if biography: command += "biography = '" + biography + "' "
        if channel_settings: command += "channel-settings = '" + channel_settings + "' "
        if display_name: command += "display_name = '" + display_name + "' "
        if room_settings: command += "room_settings = '" + generation.aes_encrypt(settings, hash) + "' "
        if settings: command += "settings = '" + generation.aes_encrypt(settings, hash) + "' "

        cursor.execute(command + " WHERE username = ?", (username,))
    except sqlite3.OperationalError:
        raise Exception("nouser")
    else:
        connection.commit()

def exists(username):
    try:
        cursor.execute("SELECT username FROM users WHERE username = ?", (username,))
    except sqlite3.OperationalError:
        return False
    else:
        return True

def check_credentials(username, password):
    hash = generation.hashed_password(password)
    try:
        return hash == cursor.execute("SELECT hash FROM users WHERE username = ?", (username,)).fetchone()[0], hash
    except sqlite3.OperationalError:
        return False

def get_hash(username):
    try:
        hash = cursor.execute("SELECT hash FROM users WHERE username = ?", (username,)).fetchone()[0]
    except sqlite3.OperationalError:
        raise Exception("nouser")
    else:
        return hash
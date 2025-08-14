import json
import sqlite3

import database.rooms as rooms
import database.sqlite_wrapper as sql
import utilities.cryptography as cryptography

def access_to_conversation(username, uuid, private_key):
    try:
        users = cryptography.aes_decrypt(cursor.execute("SELECT users FROM conversations WHERE uuid = ?", (uuid)).fetchone()[0], private_key).split(",")
    except sqlite3.OperationalError:
        return False
    else:
        return username in users

def access_to_channel(username, uuid, private_key): #WILL USE PERMISSIONS
    return True #Temporary

def access_to_room(username, uuid, private_key):
    if username in rooms.members(uuid, private_key):
        return True
    else:
        return False

def fetch_from_db(table, where, value, column="*"):
    try:
        data = cursor.execute("SELECT ? FROM ? WHERE ? = ?", (column, table, where, value)).fetchone()
    except sqlite3.OperationalError:
        return None
    else:
        return data

def verify_hash(username, hash): #WILL BE REPLACED WITH AN AUTHENTICATION SYSTEM
    try:
        json.loads(cryptography.aes_decrypt(cursor.execute("SELECT key_chain FROM users WHERE username = ?", (username,)).fetchone()[0], hash))
    except Exception:
        return False

def verify_passcode(uuid, passcode):
    try:
        result = cryptography.aes_decrypt(cursor.execute("SELECT result FROM invites WHERE uuid = ?", (uuid,)).fetchone()[0], passcode)
    except Exception:
        return False
    else:
        return result.isascii() and len(result) == 3

def verify_private_key(uuid, private_key):
    try:
        title = cryptography.rsa_decrypt(cursor.execute("SELECT title FROM rooms WHERE uuid = ?", (uuid,)).fetchone()[0], private_key)
    except Exception:
        return False
    else:
        return title.isascii()
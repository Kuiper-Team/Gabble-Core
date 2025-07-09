import sqlite3

import utilities.generation as generation
from database.connection import connection, cursor
from utilities.uuidv7 import uuid_v7

cursor.execute("""CREATE TABLE IF NOT EXISTS conversations (
uuid TEXT NOT NULL,
users TEXT NOT NULL,
public_key TEXT NOT NULL,
PRIMARY KEY (uuid))
""")

def create(username1, username2):
    key_pair = generation.rsa_generate_pair(),
    public_key = key_pair[0]
    uuid = uuid_v7().hex
    try:
        cursor.execute("INSERT INTO rooms VALUES (?, ?, ?)", (uuid, generation.rsa_encrypt(username1 + "," + username2, public_key), public_key))
    except sqlite3.OperationalError:
        raise Exception("conversationexists")
    else:
        connection.commit()

        return uuid, public_key, key_pair[1]

def delete(uuid):
    try:
        cursor.execute("DELETE FROM conversations WHERE uuid = ?", (uuid,))
    except sqlite3.OperationalError:
        raise Exception("noconversation")
    else:
        connection.commit()
#BUNUN YERİNE HASH İLE ONAYLAMA KULLANILABİLİR.
import sqlite3
from sys import path

path.append("..")

import utilities.generation as generation
from database.connection import connection, cursor
from uuid import uuid4

cursor.execute("""CREATE TABLE IF NOT EXISTS requests (
sender TEXT NOT NULL, recipient TEXT NOT NULL,
uuid TEXT NOT NULL,
type INTEGER NOT NULL,
expiry INTEGER NOT NULL,
PRIMARY KEY (uuid))
""")

#type değeri için:
#0: Arkadaşlık isteği
def send(sender, recipient, message, type, expiry, hash):
    try:
        cursor.execute("INSERT INTO requests VALUES (?, ?, ?, ?, ?, ?)", (sender, recipient, uuid4().hex, type, expiry))
    except sqlite3.OperationalError:
        raise Exception("couldntinsert")
    else:
        connection.commit()

def cancel(uuid):
    try:
        cursor.execute("DELETE FROM requests WHERE uuid = ?", (uuid,))
    except sqlite3.OperationalError:
        raise Exception("norequest")
    else:
        connection.commit()
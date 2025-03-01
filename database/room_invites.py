#BUNUN YERİNE HASH İLE ONAYLAMA KULLANILABİLİR.
import sqlite3
from sys import path

path.append("..")

from database.connection import connection, cursor
from uuid import uuid4

cursor.execute("""CREATE TABLE IF NOT EXISTS room_invites (
uuid TEXT NOT NULL,
room_uuid TEXT NOT NULL,
type INTEGER NOT NULL,
expiry INTEGER NOT NULL,
PRIMARY KEY (uuid))
""")

def create(uuid, type, expiry):
    try:
        cursor.execute("INSERT INTO invitations VALUES (?, ?, ?, ?)", (uuid4().hex, uuid, type, expiry))
    except sqlite3.OperationalError:
        raise Exception("couldntinsert")
    else:
        connection.commit()

def delete(uuid):
    try:
        cursor.execute("DELETE FROM invitations WHERE uuid = ?", (uuid))
    except sqlite3.OperationalError:
        raise Exception("noinvitation")
    else:
        connection.commit()
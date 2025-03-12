import sqlite3

import utilities.generation as generation
from database.connection import connection, cursor

cursor.execute("""CREATE TABLE IF NOT EXISTS channels (
title TEXT NOT NULL,
uuid TEXT NOT NULL,
room_uuid TEXT NOT NULL,
type INTEGER NOT NULL,
settings TEXT NOT NULL,
permissions_map TEXT NOT NULL,
tags TEXT,
PRIMARY KEY (uuid))
""")

#create yok, rooms.py'a bakınız.

def delete(uuid, room_uuid):
    try:
        cursor.execute("DELETE FROM channels WHERE uuid = ? AND room_uuid = ?", (uuid, room_uuid))
    except sqlite3.OperationalError:
        raise Exception("nochannel")
    else:
        connection.commit()

def update(): #Hazırlanacak.
    pass
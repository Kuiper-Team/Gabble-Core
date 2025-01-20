from sys import path

path.append("..")

from connection import connection, cursor

cursor.execute("CREATE TABLE IF NOT EXISTS channels (title TEXT NOT NULL, uuid TEXT NOT NULL, group_uuid TEXT NOT NULL, type INTEGER NOT NULL, settings TEXT NOT NULL, permissions_map TEXT NOT NULL, tags TEXT, PRIMARY KEY (uuid))")
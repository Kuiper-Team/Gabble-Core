from sys import path

path.append("..")

from connection import connection, cursor

cursor.execute("CREATE TABLE IF NOT EXISTS messages (message TEXT NOT NULL, uuid TEXT NOT NULL, group_uuid TEXT NOT NULL, channel_uuid TEXT NOT NULL, PRIMARY KEY (uuid))")
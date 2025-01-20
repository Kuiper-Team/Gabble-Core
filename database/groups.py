from sys import path

path.append("..")

from connection import connection, cursor

cursor.execute("CREATE TABLE IF NOT EXISTS groups (title TEXT NOT NULL, uuid TEXT NOT NULL, channels TEXT, settings TEXT NOT NULL, permissions_map TEXT NOT NULL, has_picture INTEGER NOT NULL, PRIMARY KEY (uuid))")
#"channels" formatı: kanal_türü_numarası + kanal uuid'si + virgül + ...
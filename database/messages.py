from sys import path

path.append("..")

from connection import connection, cursor

#cursor.execute("CREATE TABLE IF NOT EXISTS messages (x TEXT NOT NULL, PRIMARY KEY (x))")
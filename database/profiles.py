import sqlite3
from sys import path

path.append("..")

from connection import connection, cursor

cursor.execute("CREATE TABLE IF NOT EXISTS profiles (username TEXT NOT NULL, biography TEXT, has_picture INTEGER NOT NULL, PRIMARY KEY (username))")

def update_profile(username, biography, has_picture): #"username" değiştirilemez. (Belgelerde gerekçe yazacağım.)
    try:
        cursor.execute("UPDATE profiles SET biography = ?, has_picture = ? WHERE username = ?", (biography, 0 if has_picture == False else 1, username))
    except sqlite3.OperationalError:
        raise Exception("nouser")
    else:
        connection.commit()
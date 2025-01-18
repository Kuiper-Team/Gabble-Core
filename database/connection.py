import sqlite3
from sys import path

path.append("..")

import utilities.log as log
from config import database

connection = None
try:
    connection = sqlite3.connect("{}.db".format(database.file_name))
except sqlite3.OperationalError:
    log.failure("\"{}.db\" veri tabanına bağlanılamadı. (sqlite3.OperationalError)".format(database.file_name))
    exit(1)
else:
    log.success("\"{}.db\" veri tabanına bağlanıldı.".format(database.file_name))

cursor = connection.cursor()
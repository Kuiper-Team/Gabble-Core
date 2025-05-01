#The database file will always be saved to the same path.
import sqlite3
import sys
from os import environ

sys.path.append("..")

import utilities.log as log

path = environ.get("GABBLE_DATABASE")
try:
    connection = sqlite3.connect(path, check_same_thread=False)
except sqlite3.OperationalError:
    log.failure("Veri tabanına bağlanılamadı.")
    exit(1)
else:
    log.success("Veri tabanına bağlanıldı.")

cursor = connection.cursor()
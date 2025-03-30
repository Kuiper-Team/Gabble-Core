#The database file will always be saved to the same path.
import os
import sqlite3
from pathlib import Path

import utilities.log as log

file_name = "database.db"

try:
    connection = sqlite3.connect(os.path.join(Path.cwd(), file_name), check_same_thread=False)
except sqlite3.OperationalError:
    log.failure("\"{}\" veri tabanına bağlanılamadı.".format(file_name))
    exit(1)
else:
    log.success("\"{}\" veri tabanına bağlanıldı.".format(file_name))

cursor = connection.cursor()
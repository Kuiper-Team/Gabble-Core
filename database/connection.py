#The database file will always be saved to the same path.
import os
import sqlite3
from pathlib import Path

import utilities.log as log

file_name = "database.db"

def find_file(directory, target_file):
    for root, directories, files in os.walk(directory):
        for file in files:
            if file == target_file:
                return file

    return None

cwd = Path.cwd()
try:
    connection = sqlite3.connect(find_file(os.path.join(cwd, ".."), file_name), check_same_thread=False) #find_file doesn't work properly.
except sqlite3.OperationalError:
    log.failure("\"{}\" veri tabanına bağlanılamadı.".format(file_name))
    exit(1)
else:
    log.success("\"{}\" veri tabanına bağlanıldı.".format(file_name))

cursor = connection.cursor()
#The database file will always be saved to the same path.
import os
import sqlite3
import sys
from pathlib import Path

sys.path.append("..")

import utilities.log as log

file_name = "database.db"

def find_file(directory, target_file):
    for root, directories, files in os.walk(directory):
        for file in files:
            if file == target_file:
                return os.path.join(directory, file)

    return None

path = find_file(os.path.join(Path.cwd(), "..", "database"), file_name)
try:
    if path:
        connection = sqlite3.connect(path, check_same_thread=False) #find_file doesn't work properly.
    else:
        log.failure("\"{}\" veri tabanına bağlanılamadı.".format(file_name))
        exit(1)
except sqlite3.OperationalError:
    log.failure("\"{}\" veri tabanına bağlanılamadı.".format(file_name))
    exit(1)
else:
    log.success("\"{}\" veri tabanına bağlanıldı.".format(file_name))

cursor = connection.cursor()
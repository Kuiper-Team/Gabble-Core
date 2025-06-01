#A .env file containing the path to the database, labelled GABBLE_DATABASE_PATH, must be created in this directory.
import sqlite3
import sys
from dotenv import load_dotenv
from os import getenv

sys.path.append("..")

import utilities.log as log

load_dotenv()

try:
    connection = sqlite3.connect(getenv("GABBLE_DATABASE_PATH"), check_same_thread=False)
except Exception:
    log.failure("Could not connect to the database.")
    exit(1)
else:
    log.success("Connected to the database.")

cursor = connection.cursor()
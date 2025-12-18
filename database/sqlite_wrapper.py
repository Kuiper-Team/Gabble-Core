#A .env file containing an environmental variable for the path to the database, labelled GABBLE_DATABASE_PATH, must be created in this directory.
import sqlite3
from dotenv import load_dotenv
from os import getenv
from typing import Tuple

load_dotenv()

connection = sqlite3.connect(getenv("GABBLE_DATABASE_PATH"), check_same_thread=False) #No error handling to make the app stop when it can't connect to the database…
cursor = connection.cursor()

class C:
    def __init__(self, name, type, not_null=False):
        self.name = name
        self.type = type
        self.not_null = not_null

class Types:
    BLOB = "BLOB"
    INTEGER = "INTEGER"
    NUMERIC = "NUMERIC"
    REAL = "REAL"
    TEXT = "TEXT"

#safe refers to the exception which is raised when an exception occurs.
#condition refers to the boolean value that decides whether the query should be run or not. This feature is useful for optional parameters.

def table(name, columns: Tuple[C, ...], primary_key=None, exception=None, safe=False):
    query = f"CREATE TABLE IF NOT EXISTS {name} ("

    column_count = len(columns) - 1
    column_i = 0
    for column in columns:
        query += f"{column.name} {column.type}"
        if column.not_null: query += " NOT NULL"
        if not column_i == column_count: query += ","

        column_i += 1

    if primary_key: query += f", PRIMARY KEY ({primary_key})"

    query += ")"

    try:
        cursor.execute(query)
    except sqlite3.OperationalError as error:
        if safe: return
        if exception is not None:
            raise exception
        else:
            raise error

def select(table, where, value, column="*", exception=None, safe=False):
    try:
        data = cursor.execute(
            f"SELECT {column} FROM {table} WHERE {where} = ?",
            (value,),
        ).fetchone()
    except sqlite3.OperationalError as error:
        if safe: return
        if exception is not None:
            raise exception
        else:
            raise error
    else:
        if data is None or len(data) == 0: return None
        else: return data

def insert(table, values: Tuple, exception: str or None=None, safe=False):
    try:
        cursor.execute(f"INSERT INTO {table} VALUES ({','.join(['?'] * len(values))})", values)
    except sqlite3.OperationalError as error:
        if safe: return
        if exception is not None:
            raise Exception(exception)
        else:
            raise error
    else:
        connection.commit()

def update(table, column, assign, where, value, condition=True, exception=None, safe=False):
    if not condition: return #Abort

    try:
        cursor.execute(f"UPDATE {table} SET {column} = ? WHERE {where} = ?", (assign, value))
    except sqlite3.OperationalError as error:
        if safe: return
        if exception is not None:
            raise exception
        else:
            raise error
    else:
        connection.commit()

def delete(table, where, value, exception=None, safe=False):
    try:
        cursor.execute(f"DELETE FROM {table} WHERE {where} = ?", (value,))
    except sqlite3.OperationalError as error:
        if safe: return
        if exception is not None:
            raise exception
        else:
            raise error
    else:
        connection.commit()
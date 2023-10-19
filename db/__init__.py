import os

from tinydb import TinyDB


DB_NAME = os.environ.get("DB_NAME", "db")


def get_db() -> TinyDB:
    return TinyDB(f"{DB_NAME}.json")

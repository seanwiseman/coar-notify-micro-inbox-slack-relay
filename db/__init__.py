import os

from tinydb import TinyDB
from tinydb.storages import MemoryStorage


DB_NAME = os.environ.get("DB_NAME", "db")


def get_db() -> TinyDB:
    if TinyDB.default_storage_class is MemoryStorage:
        return TinyDB()

    return TinyDB(f"{DB_NAME}.json")

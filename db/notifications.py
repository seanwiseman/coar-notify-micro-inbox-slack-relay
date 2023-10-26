from typing import Optional

from tinydb import Query

from db import get_db
from db.models import Notification


NOTIFICATIONS = "notifications"


class NotificationDBContextManager:
    def __init__(self):
        self._db = None
        self.notifications_table = None

    def __enter__(self):
        self._db = get_db()
        self.notifications_table = self._db.table(NOTIFICATIONS)
        return self.notifications_table

    def __exit__(self, exc_type, exc_value, traceback):
        self._db.close()


async def create(notification: Notification) -> None:
    with NotificationDBContextManager() as notifications_table:
        notifications_table.insert(notification.model_dump(by_alias=True))


async def get_by_id(notification_id: str) -> Optional[Notification]:
    with NotificationDBContextManager() as notifications_table:
        notification = None

        result = notifications_table.search(Query().id == notification_id)

        if len(result) > 0:
            notification = result[0]

        return notification

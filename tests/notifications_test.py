from unittest.mock import patch, call

import pytest
from tinydb import Query

from db.notifications import create, get_by_id


@pytest.mark.asyncio
async def test_create_inserts_notification(mock_db):
    notification_data = {
        "id": "12345",
        "message": "Test notification"
    }

    with patch('db.notifications.get_db', return_value=mock_db):
        await create(notification_data)

    mock_db.table.assert_called_once_with("notifications")
    mock_db.table().insert.assert_called_once_with(notification_data)


@pytest.mark.asyncio
async def test_get_by_id_returns_notification_when_exists(mock_db):
    notification_data = {
        "id": "12345",
        "message": "Test notification"
    }

    mock_db.table().search.return_value = [notification_data]

    with patch('db.notifications.get_db', return_value=mock_db):
        result = await get_by_id("12345")

    mock_db.table.assert_has_calls([
        call("notifications"),
        call().search(Query().id == "12345")
    ])
    assert result == notification_data


@pytest.mark.asyncio
async def test_get_by_id_returns_none_when_not_exists(mock_db):
    with patch('db.notifications.get_db', return_value=mock_db):
        result = await get_by_id("nonexistent_id")

    mock_db.table.assert_called_once_with("notifications")
    assert result is None

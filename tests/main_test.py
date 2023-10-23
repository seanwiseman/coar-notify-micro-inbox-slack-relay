from unittest.mock import patch

from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


@patch("main.post_slack_message")
def test_add_notification(mock_post_slack_message, valid_notification_payload):
    response = client.post("/inbox", json=valid_notification_payload)

    assert response.status_code == 201
    assert mock_post_slack_message.called


@patch("main.post_slack_message")
def test_add_notification_invalid_payload(mock_post_slack_message,
                                          invalid_notification_payload):
    response = client.post("/inbox", json=invalid_notification_payload)

    assert response.status_code == 400
    assert not mock_post_slack_message.called


@patch("main.notifications.get_by_id")
def test_read_notification(mock_get_by_id, valid_notification_payload):
    mock_get_by_id.return_value = valid_notification_payload

    response = client.get(f"/inbox/{valid_notification_payload['id']}")

    assert response.status_code == 200
    assert response.json() == valid_notification_payload
    assert mock_get_by_id.called_once_with(valid_notification_payload["id"])


@patch("main.notifications.get_by_id")
def test_read_notification_handles_not_found(mock_get_by_id):
    invalid_notification_id = "invalid-notification-id"
    mock_get_by_id.return_value = None

    response = client.get(f"/inbox/{invalid_notification_id}")

    assert response.status_code == 404
    assert response.json() == {"detail": "Notification not found"}
    assert mock_get_by_id.called_once_with(invalid_notification_id)

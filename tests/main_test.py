from unittest.mock import patch

from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


@patch("main.post_slack_message")
def test_add_notification(mock_post_slack_message, valid_notification_payload):
    response = client.post("/inbox/", json=valid_notification_payload)

    assert response.status_code == 201
    assert mock_post_slack_message.called

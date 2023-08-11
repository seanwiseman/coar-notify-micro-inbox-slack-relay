import logging
from unittest.mock import patch

from requests.exceptions import RequestException

from slack import format_payload_into_slack_blocks, post_slack_message


class TestFormatPayloadIntoSlackBlocks:
    def test_empty_data(self):
        data = {}
        result = format_payload_into_slack_blocks(data)
        expected_text = "```{}```"
        assert result['blocks'][1]['text']['text'] == expected_text

    def test_single_key_value_pair(self):
        data = {"key": "value"}
        result = format_payload_into_slack_blocks(data)
        expected_text = '```{\n    "key": "value"\n}```'
        assert result['blocks'][1]['text']['text'] == expected_text

    def test_nested_data(self):
        data = {"parent": {"child": "value"}}
        result = format_payload_into_slack_blocks(data)
        expected_text = '```{\n    "parent": {\n        "child": "value"\n    }\n}```'
        assert result['blocks'][1]['text']['text'] == expected_text


@patch('slack.requests.post')
def test_post_slack_message_success(mocked_requests_post, caplog):
    mocked_requests_post.return_value.status_code = 201
    payload = {"message": "test"}

    with caplog.at_level(logging.INFO):
        post_slack_message(payload)
        assert "Message posted successfully to Slack." in caplog.text


@patch('slack.requests.post')
def test_post_slack_message_failure(mocked_requests_post, caplog):
    mocked_requests_post.return_value.status_code = 400
    payload = {"message": "test"}

    with caplog.at_level(logging.INFO):
        post_slack_message(payload)
        assert "Failed to post message to Slack." in caplog.text


@patch('slack.requests.post')
def test_post_slack_message_exception(mocked_requests_post, caplog):
    mocked_requests_post.side_effect = RequestException("Test exception")
    payload = {"message": "test"}

    with caplog.at_level(logging.INFO):
        post_slack_message(payload)
        assert "An error occurred while trying to post the message to Slack." in caplog.messages[0]

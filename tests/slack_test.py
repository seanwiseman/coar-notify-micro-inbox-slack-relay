import json
import logging
from unittest.mock import patch

import pytest
from requests.exceptions import RequestException

from slack import (
    format_payload_into_slack_blocks,
    format_review_offer_payload_into_slack_blocks,
    get_formatter_for_payload,
    post_slack_message,
)


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


@pytest.mark.parametrize(
    "payload, expected",
    [
        (
                {"type": ["Offer", "coar-notify", "ReviewAction"]},
                format_review_offer_payload_into_slack_blocks
        ),
        (
                {"type": ["Offer", "coar-notify", "AcceptAction"]},
                format_payload_into_slack_blocks
        ),
        (
                {"type": ["Offer", "coar-notify", "AnnounceAction"]},
                format_payload_into_slack_blocks
        ),
        (
                {"type": ["Offer", "coar-notify", "InvalidAction"]},
                format_payload_into_slack_blocks
        ),
        (
                {"message": "test"},
                format_payload_into_slack_blocks
        ),
        (
                {},
                format_payload_into_slack_blocks
        ),
    ])
def test_get_formatter_for_payload_returns_default(payload, expected):
    assert get_formatter_for_payload(payload) == expected


def test_format_review_offer_payload_into_slack_blocks_success():
    payload = {
        "id": "10.1111/234567",
        "updated": "2023-08-09T17:01:32.340000",
        "@context": [
            "https://www.w3.org/ns/activitystreams",
            "https://purl.org/coar/notify"
        ],
        "type": [
            "Offer",
            "coar-notify:ReviewAction"
        ],
        "origin": {
            "id": "https://www.repo.org",
            "inbox": "https://api.repo.org/inbox",
            "type": "Service"
        },
        "target": {
            "id": "https://www.review-service.org",
            "inbox": "https://api.review-service.org/inbox",
            "type": "Service"
        },
        "object": {
            "id": "10.1111/234567",
            "ietf:cite-as": "https://doi.org/10.1111/234567",
        },
        "actor": {
            "id": "https://orcid.org/0001-0002-0003-0004",
            "type": "Person",
            "name": "John Doe"
        }
    }

    expected = {
        "blocks": [
            {
                "type": "header",
                "text": {
                    "text": "COAR Notification: Review Offer",
                    "type": "plain_text"
                },
            },
            {
                "type": "divider"
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "For: ""<https://doi.org/10.1111/234567|10.1111/234567>",
                },
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "From: ""<https://orcid.org/0001-0002-0003-0004|John Doe>",
                },
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "Sent via: <https://www.review-service.org>",
                },
            },
            {
                "type": "context",
                "elements": [
                    {
                        "type": "plain_text",
                        "text": "Detail:",
                    }
                ],
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"```{json.dumps(payload, indent=4)}```",
                },
            },
            {
                "type": "divider"
            }
        ]
    }
    assert format_review_offer_payload_into_slack_blocks(payload) == expected

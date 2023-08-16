import os
import json
import logging

import requests
from requests.exceptions import RequestException

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SLACK_CHANNEL = os.environ.get("SLACK_CHANNEL")
SLACK_API_TOKEN = os.environ.get("SLACK_API_TOKEN")
SLACK_POST_MESSAGE_API_URL = "https://slack.com/api/chat.postMessage"


def format_review_offer_payload_into_slack_blocks(data: dict) -> dict:
    actor_name = data.get("actor", {}).get("name", "the author")
    doi = data.get("object", {}).get("id", "")

    return {
        "blocks": [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"A new request has come in for a PREreview of "
                            f"<https://doi.org/{doi}|{doi}> by {actor_name} on bioRxiv."
                },
                "accessory": {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "Write a PREreview"
                    },
                    "url": f"https://sandbox.prereview.org/preprints/"
                           f"doi-{doi.replace('/', '-')}/write-a-prereview"
                }
            }
        ]
    }


def format_payload_into_slack_blocks(data: dict) -> dict:
    return {
        "blocks": [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": "COAR Notification",
                },
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"```{json.dumps(data, indent=4)}```",
                },
            },
            {
                "type": "divider",
            },
        ],
    }


FORMATTERS = {
    "Offer:coar-notify:ReviewAction": format_review_offer_payload_into_slack_blocks
}


def get_formatter_for_payload(payload: dict) -> callable:
    return FORMATTERS.get(":".join(payload.get("type", "")), format_payload_into_slack_blocks)


def post_slack_message(payload: dict) -> None:
    try:
        formatter = get_formatter_for_payload(payload)

        response = requests.post(
            url=SLACK_POST_MESSAGE_API_URL,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {SLACK_API_TOKEN}",
            },
            json={
                "channel": SLACK_CHANNEL,
                **formatter(payload),
            },
            timeout=(10, 10),
        )
        response.raise_for_status()

        if response.status_code == 201:
            logger.info("Message posted successfully to Slack.")
        else:
            logger.warning(f"Failed to post message to Slack. Response: {response.json()}")

    except RequestException:
        logger.exception("An error occurred while trying to post the message to Slack.")

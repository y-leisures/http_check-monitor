import os

import requests
from requests import Response

DEFAULT_WEBHOOK_URL = 'https://hooks.slack.com/services/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'


def notify_to_slack(payload: dict) -> Response:
    webhook_url = os.getenv('SLACK_WEBHOOK_URL', DEFAULT_WEBHOOK_URL)
    response: Response = requests.post(
        webhook_url,
        json=payload,
    )
    return response

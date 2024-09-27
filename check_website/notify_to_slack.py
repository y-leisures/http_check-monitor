import os

import requests

from requests import Response


def notify_to_slack(payload: dict) -> Response:
    webhook_url = os.getenv('SLACK_WEBHOOK_URL')
    response: Response = requests.post(
        webhook_url,
        json=payload,
    )
    return response

import dataclasses
import json
import os
from datetime import datetime
from urllib.error import HTTPError

import boto3
import requests
import twitter
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

# from boto3.dynamodb.conditions import Key
from common import get_secret


@dataclasses.dataclass
class FailureEven:
    eventTime: int
    failing_url: str
    completionTime: int = 0
    resolved: bool = False


def check_health(url: object, timeout: int = 30) -> bool:
    retries = Retry(total=5, backoff_factor=1, status_forcelist=[500, 502, 503, 504])
    s = requests.session()
    s.mount(prefix='http', adapter=HTTPAdapter(max_retries=retries))
    headers = {
        'From': 'Request from aws lambda function',
    }

    try:
        resp = s.get(url, headers=headers, timeout=timeout)
        resp.raise_for_status()
        return True
    except HTTPError as _:
        return False


def record_failure_event(failing_url: str):
    resource = boto3.resource('dynamodb')
    table = resource.Table('bms-monitoring-events-development')

    now = datetime.now().timestamp()
    row = dataclasses.asdict(FailureEven(eventTime=int(now), failing_url=failing_url))
    table.put_item(Item=row)


def main(monitor_url: str):
    secrets = get_secret()
    api = twitter.Api(
        consumer_key=secrets['CONSUMER_KEY'], consumer_secret=secrets['CONSUMER_SECRET'],
        access_token_key=secrets['ACCESS_TOKEN_KEY'], access_token_secret=secrets['ACCESS_TOKEN_SECRET']
    )

    MESSAGE_TEMPLATE = '[{}] {} is down now. Please reboot the server! @uokada'
    message = MESSAGE_TEMPLATE.format(datetime.now().isoformat()[:19], monitor_url)
    post_success = False
    counter = 0
    while post_success == False:
        try:
            result: twitter.Status = api.PostUpdate(status=message)
            # pprint(result.id)
            post_success = True
        except twitter.error.TwitterError as te:
            counter += 1
            if counter >= 3:
                # Give up the message post
                post_success = True
    return 0


def lambda_handler(event, context):
    """Sample pure Lambda function

    Parameters
    ----------
    event: dict, required
        API Gateway Lambda Proxy Input Format

        Event doc: https://docs.aws.amazon.com/apigateway/latest/developerguide/set-up-lambda-proxy-integrations.html#api-gateway-simple-proxy-for-lambda-input-format

    context: object, required
        Lambda Context runtime methods and attributes

        Context doc: https://docs.aws.amazon.com/lambda/latest/dg/python-context-object.html

    Returns
    ------
    API Gateway Lambda Proxy Output Format: dict

        Return doc: https://docs.aws.amazon.com/apigateway/latest/developerguide/set-up-lambda-proxy-integrations.html
    """

    monitor_url = os.getenv("MONITOR_URL")

    result: bool = check_health(monitor_url)
    if not result:
        record_failure_event(failing_url=monitor_url)
        main(monitor_url=monitor_url)
        return {
            "statusCode": 200,
            "body": json.dumps({
                "message": "{} is down! Please contact to administrator!".format(monitor_url),
                # "location": ip.text.replace("\n", "")
            }),
        }
    else:
        return {
            "statusCode": 200,
            "body": json.dumps({
                "message": "{} is running!".format(monitor_url),
                # "location": ip.text.replace("\n", "")
            }),
        }

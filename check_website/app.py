import dataclasses
import json
import os
import uuid
from datetime import datetime
from urllib.error import HTTPError

import boto3
import requests
import twitter
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

from common import get_secret

S3_BUCKET = os.getenv('S3_BUCKET', 'y-bms-tokyo')
OBJECT_KEY_ON_S3 = os.getenv('OBJECT_KEY_ON_S3', 'monitor.db')


@dataclasses.dataclass
class FailureEven:
    eventTime: int
    failing_url: str
    completionTime: int = 0
    resolved: bool = False


class s3objectHandler(object):
    # see: https://stackoverflow.com/questions/3774328/implementing-use-of-with-object-as-f-in-custom-class-in-python

    def __init__(self, bucket: str, object_file: str):
        self.bucket = bucket
        self.object_file = object_file
        self.tmp_filename = self._generate_tmp_filename()
        self._client = boto3.client('s3')

    def __enter__(self):
        self.fd = self._fetch_file()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._put_file()

    def _fetch_file(self):
        response: dict = self._client.get_object(Bucket=self.bucket, Key=self.object_file)
        if 'HTTPStatusCode' in response and response['HTTPStatusCode'] == 200:
            if 'Body' in response:
                contents = response['Body'].read()
                with open(self.tmp_filename, 'wb') as fh:
                    fh.write(contents)
                return open(self.tmp_filename, 'r+b')
        raise RuntimeError(f'Failed to open(s3://{self.bucket}/{self.object_file})')

    def _put_file(self):
        response = self._client.put_object(
            Body=self.tmp_filename,
            Bucket=self.bucket, Key=self.object_file
        )
        if 'HTTPStatusCode' in response and response['HTTPStatusCode'] == 200:
            return
        raise RuntimeError(f'Failed to put (s3://{self.bucket}/{self.object_file})')

    @staticmethod
    def _generate_tmp_filename() -> str:
        return str(uuid.uuid4())


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

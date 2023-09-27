import dataclasses
import json
import os
import sqlite3
import uuid
from collections import namedtuple
from sqlite3 import Cursor
from urllib.error import HTTPError

import boto3
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

from notify_to_slack import notify_to_slack

S3_BUCKET = os.getenv('S3_BUCKET', 'y-bms-tokyo')
OBJECT_KEY_ON_S3 = os.getenv('OBJECT_KEY_ON_S3', 'http_monitor/monitor.db')


def namedtuple_factory(cursor, row):
    fields = [column[0] for column in cursor.description]
    cls = namedtuple("Row", fields)
    return cls._make(row)


@dataclasses.dataclass
class FailureEven:
    eventTime: int
    failing_url: str
    completionTime: int = 0
    resolved: bool = False


class SqliteOnS3Handler(object):
    # see: https://stackoverflow.com/questions/3774328/implementing-use-of-with-object-as-f-in-custom-class-in-python

    def __init__(self, bucket: str, object_file: str):
        self.bucket = bucket
        self.object_file = object_file
        self.tmp_filename = self._generate_tmp_filename()
        self._client = boto3.client('s3')

    def __enter__(self):
        self.connection = self._fetch_file()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.connection.commit()
        self.connection.close()
        self._put_file()

    def _fetch_file(self):
        try:
            response: dict = self._client.get_object(Bucket=self.bucket, Key=self.object_file)
            if 'Body' in response:
                contents = response['Body'].read()
                with open(self.tmp_filename, 'wb') as fh:
                    fh.write(contents)
                return sqlite3.connect(self.tmp_filename)
        except RuntimeError as e:
            print(e)
            raise RuntimeError(f'Failed to open(s3://{self.bucket}/{self.object_file})')

    def _put_file(self):
        with open(self.tmp_filename, 'rb') as fh:
            response = self._client.put_object(
                Body=fh.read(),
                Bucket=self.bucket, Key=self.object_file
            )
        if 'ResponseMetadata' in response and \
                'HTTPStatusCode' in response['ResponseMetadata'] and \
                response['ResponseMetadata']['HTTPStatusCode'] == 200:
            return
        else:
            print(response)
            raise RuntimeError(f'Failed to put (s3://{self.bucket}/{self.object_file})')

    @staticmethod
    def _generate_tmp_filename() -> str:
        return '/tmp/' + str(uuid.uuid4())


def execute_ddl_queries(cursor: Cursor) -> None:
    queries = {
        "current_status": """
        CREATE TABLE IF NOT EXISTS current_status
            (
                id         INTEGER PRIMARY KEY,
                status     VARCHAR  default 'up'              not null,
                updated_at DATETIME default CURRENT_TIMESTAMP not null
            )
        """,
        "status_history": """
        CREATE TABLE IF NOT EXISTS status_history
            (
                id         INTEGER  primary key,
                new_status VARCHAR  default 'up'              not null,
                created_at DATETIME default CURRENT_TIMESTAMP not null
            )
        """,
    }
    for table, ddl in queries.items():
        print("Execute the DDL for {}".format(table))
        cursor.execute(ddl)
    return


def record_status_change(cursor: Cursor, new_status: str) -> None:
    query = "INSERT INTO status_history (new_status) VALUES ('{}')".format(new_status)
    response = cursor.execute(query)
    if response.rowcount != 1:
        raise RuntimeError('Fail to insert into status_history')
    return


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
    except (HTTPError, ConnectionError) as e:
        print(e)
        return False
    except Exception as e:
        print(e)
        return False


def record_failure_event(bucket: str = S3_BUCKET, object_file: str = OBJECT_KEY_ON_S3):
    with SqliteOnS3Handler(bucket=bucket, object_file=object_file) as db:
        db.connection.row_factory = namedtuple_factory
        cursor: Cursor = db.connection.cursor()

        execute_ddl_queries(cursor)

        # Fetch current status and then update the record
        current_status = cursor.execute('select * FROM current_status WHERE id = 1').fetchone()
        print(current_status)
        if current_status.status == 'up':
            query = "UPDATE current_status SET status = 'down', updated_at = current_timestamp WHERE id = 1"
            response = cursor.execute(query)
            if response.rowcount != 1:
                raise RuntimeError('Fail to update the record')
            record_status_change(cursor, 'down')

            # Notify to slack
            monitor_url = os.getenv("MONITOR_URL")
            payload = {
                "text": "{} is down! Please contact to administrators! ⚠️".format(monitor_url),
            }
            notify_to_slack(payload)
        else:
            query = "UPDATE current_status SET updated_at = current_timestamp WHERE id = 1"
            response = cursor.execute(query)
            if response.rowcount != 1:
                raise RuntimeError('Fail to update the record')
        cursor.close()


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
    if not result:  # When the server is down
        record_failure_event()
        payload = {
            "text": "{} is down! Please contact to administrators! ⚠️".format(monitor_url),
        }
        return {
            "statusCode": 200,
            "body": json.dumps(payload),
        }
    else:
        with SqliteOnS3Handler(bucket=S3_BUCKET, object_file=OBJECT_KEY_ON_S3) as db:
            db.connection.row_factory = namedtuple_factory
            cursor: Cursor = db.connection.cursor()

            execute_ddl_queries(cursor)

            # Fetch current status and then update the record
            current_status = cursor.execute('select * FROM current_status WHERE id = 1').fetchone()
            if current_status.status == 'up':
                query = "UPDATE current_status SET updated_at = current_timestamp WHERE id = 1"
            else:
                query = "UPDATE current_status SET status = 'up', updated_at = current_timestamp WHERE id = 1"
                record_status_change(cursor, 'up')
                payload = {
                    "text": "{} is back to normal! ✅".format(monitor_url),
                }
                notify_to_slack(payload)
            response = cursor.execute(query)
            if response.rowcount != 1:
                raise RuntimeError('Fail to update the record')
            # new_status = cursor.execute('select * FROM current_status WHERE id = 1').fetchone()
            cursor.close()

        return {
            "statusCode": 200,
            "body": json.dumps({
                "text": "{} is running!".format(monitor_url),
                #  "location": ip.text.replace("\n", "")
            }),
        }

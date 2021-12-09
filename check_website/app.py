import base64
import json
import os
from datetime import datetime
from urllib.error import HTTPError

import boto3
import requests
import twitter
from botocore.exceptions import ClientError
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry


def check_health(url: object, timeout: int = 30) -> bool:
    retries = Retry(total=5, backoff_factor=1, status_forcelist=[500, 502, 503, 504])
    s = requests.session()
    s.mount(prefix='https://', adapter=HTTPAdapter(max_retries=retries))
    headers = {
        'From': 'Request from aws lambda function',
    }

    try:
        resp = s.get(url, headers=headers, timeout=timeout)
        resp.raise_for_status()
        return True
    except HTTPError as _:
        return False


def get_secret() -> object:
    secret_name = "TwitterApiTokenForBms"
    region_name = "us-east-1"

    # Create a Secrets Manager client
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name
    )

    # In this sample we only handle the specific exceptions for the 'GetSecretValue' API.
    # See https://docs.aws.amazon.com/secretsmanager/latest/apireference/API_GetSecretValue.html
    # We rethrow the exception by default.

    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name
        )
    except ClientError as e:
        if e.response['Error']['Code'] == 'DecryptionFailureException':
            # Secrets Manager can't decrypt the protected secret text using the provided KMS key.
            # Deal with the exception here, and/or rethrow at your discretion.
            raise e
        elif e.response['Error']['Code'] == 'InternalServiceErrorException':
            # An error occurred on the server side.
            # Deal with the exception here, and/or rethrow at your discretion.
            raise e
        elif e.response['Error']['Code'] == 'InvalidParameterException':
            # You provided an invalid value for a parameter.
            # Deal with the exception here, and/or rethrow at your discretion.
            raise e
        elif e.response['Error']['Code'] == 'InvalidRequestException':
            # You provided a parameter value that is not valid for the current state of the resource.
            # Deal with the exception here, and/or rethrow at your discretion.
            raise e
        elif e.response['Error']['Code'] == 'ResourceNotFoundException':
            # We can't find the resource that you asked for.
            # Deal with the exception here, and/or rethrow at your discretion.
            raise e
    else:
        # Decrypts secret using the associated KMS CMK.
        # Depending on whether the secret is a string or binary, one of these fields will be populated.
        if 'SecretString' in get_secret_value_response:
            secret = get_secret_value_response['SecretString']
            return json.loads(secret)
        else:
            decoded_binary_secret = base64.b64decode(get_secret_value_response['SecretBinary'])


def main():
    secrets = get_secret()
    api = twitter.Api(
        consumer_key=secrets['CONSUMER_KEY'], consumer_secret=secrets['CONSUMER_SECRET'],
        access_token_key=secrets['ACCESS_TOKEN_KEY'], access_token_secret=secrets['ACCESS_TOKEN_SECRET']
    )

    MESSAGE_TEMPLATE = '[{}] http://b-ms.info/ is down now. Please reboot the server! @uokada'
    message = MESSAGE_TEMPLATE.format(datetime.now().isoformat()[:19])
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
        main()
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

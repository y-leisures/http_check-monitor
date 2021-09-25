import json
import os

import requests

ACCESS_TOKEN = os.environ["LINE_ACCESS_TOKEN"]
HEADERS = {"Authorization": "Bearer %s" % ACCESS_TOKEN}
URL = "https://notify-api.line.me/api/notify"


def call_line_notify_api():
    message = "Hello World! from AWS lambda"
    data = {'message': message}
    requests.post(URL, headers=HEADERS, data=data)


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

    call_line_notify_api()

    return {
        "statusCode": 200,
        "body": json.dumps({
            "message": "hello world",
        }),
    }

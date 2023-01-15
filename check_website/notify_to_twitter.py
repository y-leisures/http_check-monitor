from datetime import datetime

import twitter

from common import get_secret


@DeprecationWarning
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
            post_success = True
        except twitter.error.TwitterError as te:
            counter += 1
            if counter >= 3:
                # Give up the message post
                post_success = True
    return 0

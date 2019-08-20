import requests

PUSHOVER_API_URL = 'https://api.pushover.net/1/messages.json'


class PushNotification:
    def __init__(self, args):
        self.user_key = args.usr
        self.api_token = args.app

    async def send(self, title, message, url):
        payload = {
            'token': self.api_token,
            'user': self.user_key,
            'title': title,
            'message': message,
            'url': url
        }

        requests.post(url=PUSHOVER_API_URL, json=payload)

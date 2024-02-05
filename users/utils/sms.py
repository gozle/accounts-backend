import os
import hmac
import time
import uuid
import base64
import hashlib
import requests


API_URL = os.getenv('API_URL')
USER = os.getenv('SMS_USER')
SECRET = os.getenv('SMS_SECRET')

MIN_VALUE = 10000
MAX_VALUE = 99999


def get_cleaned_phone_number(number):
    number = number[1:] if number[0] == '+' else number
    return number


def generate_hmac(key, message):
    key = base64.b64decode(key)
    msg = message.encode('utf-8')
    h = hmac.new(key, msg, hashlib.sha256).digest()
    return base64.b64encode(h)


class SMS:
    def __init__(self, text, dest):
        self.text = text
        self.dest = dest

    @staticmethod
    def _send_message(user, msg_id, dest, text, secret):
        ts = int(time.time())
        msg = f'{user}:{msg_id}:{dest}:{text}:{ts}'
        req_hmac = generate_hmac(secret, msg)
        return requests.post(API_URL + user + '/send', data={
            'msg-id': msg_id,
            'dest': dest,
            'text': text,
            'ts': ts,
            'hmac': req_hmac
        })

    def send(self):
        dest = get_cleaned_phone_number(self.dest)
        rv = self._send_message(user=USER, msg_id=uuid.uuid4(), dest=dest, text=self.text, secret=SECRET)
        return {"status_code": rv.status_code, "content": rv.content}

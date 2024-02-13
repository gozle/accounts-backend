import jwt
from django.conf import settings
from datetime import datetime, timedelta


def generate_verification_token(method, user_identifier):
    expiration_time = datetime.utcnow() + timedelta(minutes=5)
    payload = {
        'method': method,
        'user_identifier': user_identifier,
        'exp': expiration_time,
    }
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')
    return token


def parse_verification_token(token):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

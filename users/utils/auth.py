import jwt
import datetime
from random import randint, choice
from django.conf import settings
from datetime import datetime, timedelta
from users.utils.sms import MIN_VALUE, MAX_VALUE


def generate_verification_code():
    code = randint(MIN_VALUE, MAX_VALUE)
    return code


def generate_token(timeout: timedelta, **kwargs):
    expiration_time = datetime.utcnow() + timeout
    payload = {
        **kwargs,
        'exp': expiration_time,
    }
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')
    return token


def parse_token(token):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


def email_exists(email):
    if User.objects.filter(email=email).exists():
        return True
    return False


def generate_unique_email_suggestions(first_name, last_name, birthday):
    first_name = first_name.lower() if name else ''
    last_name = last_name.lower() if last_name else ''

    day = birthday.strftime("%d")
    month = birthday.strftime('%m')
    year = birthday.strftime('%Y')

    primary_suggestions = [
        (first_name, last_name),
        (first_name, last_name, year),
        (first_name, last_name, year[2:]),
    ]
    additional_suggestions = [
        (first_name, day, month, year[2:]),
        (first_name, day, month, year),
    ]
    random_suggestions = [
        (first_name, last_name),
        (first_name,)
    ]

    if last_name:
        primary_suggestions.extend([
            (first_name, year),
            (first_name, year[2:]),
            (last_name, first_name, year),
            (last_name, first_name, year[2:]),
            (last_name, first_name),
            (last_name, year),
            (last_name, year[2:]),
        ])
        additional_suggestions.extend([
            (first_name[0], last_name, year),
            (first_name[0], last_name, year[2:]),
            (last_name[0], first_name, year),
            (last_name[0], first_name, year[2:]),
        ])
        random_suggestions.extend([
            (last_name, first_name),
            (last_name,)
        ])

    primary_suggestions = [f"{''.join(combination)}" for combination in primary_suggestions]
    additional_suggestions = [f"{''.join(combination)}" for combination in additional_suggestions]
    random_suggestions = [f"{''.join(combination)}" for combination in random_suggestions]

    unique_suggestions = [email for email in primary_suggestions + additional_suggestions if
                          not email_exists(email)][:4]

    while len(unique_suggestions) < 4:
        random_suggestion_prefix = choice(random_suggestions)
        random_suggestion = f'{random_suggestion_prefix}{randint(1, 99)}'
        if not email_exists(random_suggestion):
            unique_suggestions.append(random_suggestion)

    return unique_suggestions

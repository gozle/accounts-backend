import logging

from celery import shared_task
from apps.users import SMS

logger = logging.getLogger('celery')


@shared_task
def send_email(email, subject, message):
    return {'email': email, 'subject': subject, 'message': message}


@shared_task
def send_sms(phone_number, message):
    sms = SMS(
        text=message,
        dest=phone_number
    )
    response = sms.send()
    data = {'status_code': response.get('status_code'), 'message': response.get('content'), 'text': sms.text,
            'phone_number': phone_number}
    return data

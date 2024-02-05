import json
from .base import *


DEBUG = True
BASE_URL = os.getenv('BASE_URL')
ALLOWED_HOSTS = json.loads(os.getenv('ALLOWED_HOSTS', '[]'))

# Email config
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.getenv('EMAIL_HOST')
EMAIL_PORT = os.getenv('EMAIL_PORT', 25)
EMAIL_USE_TLS = os.getenv('EMAIL_USE_TLS')
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')
EMAIL_DEFAULT_NOTIFIER = os.getenv('EMAIL_DEFAULT_NOTIFIER')

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': os.getenv('POSTGRES_DATABASE_NAME'),
        'USER': os.getenv('POSTGRES_USER'),
        'PASSWORD': os.getenv('POSTGRES_PASSWORD'),
        'HOST': os.getenv('POSTGRES_HOST'),
        'PORT': os.getenv('POSTGRES_PORT'),
    }
}


CORS_ALLOWED_HEADERS = [

]

CORS_ALLOWED_ORIGINS = [

]

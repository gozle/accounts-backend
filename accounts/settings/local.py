import json
import datetime
from .base import *


DEBUG = True
PROJECT_NAME = os.environ.get('PROJECT_NAME', 'Accounts')
ALLOWED_HOSTS = json.loads(os.getenv('ALLOWED_HOSTS', '[]'))

BASE_URL = os.getenv('BASE_URL')
LOGIN_URL = os.getenv('LOGIN_URL', '/admin/login')

# Media files (Avatars, thumbnails, documents)
MEDIA_ROOT = 'media/'
MEDIA_URL = '/media/'

# Static files (CSS, JavaScript, Images)
STATIC_ROOT = 'static/'
STATIC_URL = '/static/'

# Email config
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.getenv('EMAIL_HOST')
EMAIL_PORT = os.getenv('EMAIL_PORT', 25)
EMAIL_USE_TLS = os.getenv('EMAIL_USE_TLS')
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')
EMAIL_DEFAULT_NOTIFIER = os.getenv('EMAIL_DEFAULT_NOTIFIER')


REGISTRATION_TOKEN_HEADER = 'G-Token'
REGISTRATION_TOKEN_TIMEOUT = 60 * 10
REGISTRATION_CODE_TIMEOUT = 60 * 3

AVATAR_SIZE = 128
AVATAR_FONT = os.path.join(STATIC_ROOT, 'fonts/product-sans/Product Sans Regular.ttf')


OAUTH2_PROVIDER = {
    # Token expiration settings
    'ACCESS_TOKEN_EXPIRE_SECONDS': 60 * 5,
    'REFRESH_TOKEN_EXPIRE_SECONDS': 60 * 60 * 24 * 15,

    # Allowed grant types
    'ALLOWED_GRANT_TYPES': [
        'authorization_code',
        'password',
        'refresh_token',
        'client_credentials',
    ],

    # Token scopes
    'SCOPES': {
        'profile.read': 'Read profile scope',
        'write': 'Write scope',
        'custom_scope': 'Custom scope description',
    }
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": datetime.timedelta(minutes=5),
    "REFRESH_TOKEN_LIFETIME": datetime.timedelta(days=15),
    "AUTH_HEADER_TYPES": ("Bearer", ),
}


# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

CACHE = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379',  # Adjust this based on your Redis configuration
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}

CORS_ALLOWED_HEADERS = [

]

CORS_ALLOWED_ORIGINS = [

]

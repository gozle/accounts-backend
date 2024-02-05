import os
import datetime
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv('DJANGO_SECRET_KEY', 'secret_key')

INSTALLED_APPS = [
    # my apps
    'users',

    # extras
    'jet',
    'jet.dashboard',
    'drf_yasg',
    'rest_framework',
    'corsheaders',
    'django_user_agents',
    'oauth2_provider',
    'rest_framework_simplejwt',

    # default
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.admin',
]

MIDDLEWARE = [
    'django_user_agents.middleware.UserAgentMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'accounts.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR.parent / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'accounts.wsgi.application'

# Password validation
# https://docs.djangoproject.com/en/4.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
# https://docs.djangoproject.com/en/4.1/topics/i18n/

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

MEDIA_ROOT = 'media/'
MEDIA_URL = 'media/'

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.1/howto/static-files/

STATIC_URL = 'static/'
STATIC_ROOT = 'static/'

OAUTH2_PROVIDER = {
    # Token expiration settings
    'ACCESS_TOKEN_EXPIRE_SECONDS': 60 * 5,  # Access token expiration time in seconds (5 min)
    'REFRESH_TOKEN_EXPIRE_SECONDS': 60 * 60 * 24 * 15,  # Refresh token expiration time in seconds (30 days)

    # Allowed grant types
    'ALLOWED_GRANT_TYPES': [
        'authorization_code',
        'password',
        'refresh_token',
        'client_credentials',
    ],

    # Token scopes
    'SCOPES': {
        'read': 'Read scope',
        'write': 'Write scope',
        'custom_scope': 'Custom scope description',
    }
}

AUTH_USER_MODEL = "users.User"

# Default primary key field type
# https://docs.djangoproject.com/en/4.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        "oauth2_provider.contrib.rest_framework.OAuth2Authentication",
    ]
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": datetime.timedelta(minutes=5),
    "REFRESH_TOKEN_LIFETIME": datetime.timedelta(days=15),
    "AUTH_HEADER_TYPES": ("Bearer",),
}

LOGIN_URL = "/auth/login/"

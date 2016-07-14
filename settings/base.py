'''
https://docs.djangoproject.com/en/1.9/ref/settings/
'''
import pathlib

from django.utils.translation import ugettext_lazy as _

import dj_database_url
from kombu import Exchange, Queue

from .env import env

BASE_DIR = pathlib.Path(__file__).parent.parent
SETTINGS_DIR = BASE_DIR / 'settings'
APPS_DIR = BASE_DIR / 'apps'

ALLOWED_HOSTS = ['*']  # Host checking done by web server.
ROOT_URLCONF = 'apps.urls'
WSGI_APPLICATION = 'apps.wsgi.application'
AUTH_USER_MODEL = 'users.User'
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.PBKDF2PasswordHasher',
]

# Sites
URL = env('URL')
FRONT_URL = env('FRONT_URL')

# Mail
EMAIL_BACKEND = 'djmail.backends.default.EmailBackend'
DJMAIL_MAX_RETRY_NUMBER = 3

INSTALLED_APPS = [
    # Django
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Third party
    'rest_framework',
    'rest_framework.authtoken',
    'djmail',
    'corsheaders',
    'avatar',
    'easy_thumbnails',
    'django_jinja',
    'crispy_forms',

    # Apps
    'apps.api',
    'apps.base',
    'apps.users',
]

MIDDLEWARE_CLASSES = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

TEMPLATES = [
    {
        'BACKEND': 'django_jinja.backend.Jinja2',
        'DIRS': [str(APPS_DIR / 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'match_extension': '.j2',
            'constants': {
                'URL': URL,
                'FRONT_URL': FRONT_URL,
            },
        }
    },
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [str(APPS_DIR / 'templates')],
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


# Database
# https://docs.djangoproject.com/en/1.9/ref/settings/#databases
# https://github.com/kennethreitz/dj-database-url#url-schema
DATABASES = {}
DATABASES['default'] = dj_database_url.parse(env('DATABASE_URL'))


# Internationalization
# https://docs.djangoproject.com/en/1.9/topics/i18n/
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True
LANGUAGES = [
    ('en', _('English')),
]

# For reverse proxying
USE_X_FORWARDED_HOST = True
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTOCOL", "https")

# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'formatters': {
        'simple': {
            'format': '[%(name)s] [%(levelname)s] %(message)s'
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },
    },
    'loggers': {
    }
}

# Allow requests from any domain.
CORS_ORIGIN_ALLOW_ALL = True

# Rest Framework
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 30,
    'DEFAULT_VERSIONING_CLASS': 'rest_framework.versioning.NamespaceVersioning',
    'ORDERING_PARAM': 'order_by',
    'TEST_REQUEST_DEFAULT_FORMAT': 'json',
}

# Avatars
AVATAR_GRAVATAR_DEFAULT = 'retro'
AVATAR_STORAGE_DIR = 'user-avatars'
AVATAR_MAX_AVATARS_PER_USER = 1
AVATAR_AUTO_GENERATE_SIZES = [1024, 64]

# Celery
# http://docs.celeryproject.org/en/latest/configuration.html
BROKER_URL = env('CELERY_BROKER_URL')
CELERY_QUEUES = (
    Queue('default', Exchange('default'), routing_key='default'),
)
CELERY_DEFAULT_QUEUE = 'default'
CELERY_DEFAULT_EXCHANGE_TYPE = 'direct'
CELERY_DEFAULT_ROUTING_KEY = 'default'
CELERY_TASK_SERIALIZER = 'pickle'  # this is default but required because of a bug in djmail https://github.com/bameda/djmail/issues/36
CELERYBEAT_SCHEDULE = {
}

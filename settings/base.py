'''
https://docs.djangoproject.com/en/1.9/ref/settings/
'''
import pathlib
from datetime import timedelta

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

# Auth
AUTH_USER_MODEL = 'users.User'
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
]
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.PBKDF2PasswordHasher',
]

# Sites
URL = env('URL')
FRONT_URL = env('FRONT_URL')
FRONT_CHANGE_EMAIL_CONFIRM_URL = FRONT_URL + '/change-email/{id}/{token}'
FRONT_CHANGE_EMAIL_VERIFY_URL = FRONT_URL + '/change-email-verify/{id}/{token}'
FRONT_CONFIRM_EMAIL_URL = FRONT_URL + '/confirm-email/{id}/{token}'

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
    'social.apps.django_app.default',
    'rest_social_auth',
    'fsm_admin',

    # Base
    'apps.api',
    'apps.base',
    'apps.referrals',
    'apps.social_auth_cache',
    'apps.users',

    # Project
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

DATA_UPLOAD_MAX_MEMORY_SIZE = None
DATA_UPLOAD_MAX_NUMBER_FIELDS = None

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
    'SEARCH_PARAM': 'q',
    'TEST_REQUEST_DEFAULT_FORMAT': 'json',
}

# Avatars
AVATAR_GRAVATAR_DEFAULT = 'retro'
AVATAR_STORAGE_DIR = 'user-avatars'
AVATAR_CLEANUP_DELETED = True
AVATAR_MAX_AVATARS_PER_USER = 1
AVATAR_AUTO_GENERATE_SIZES = [1024, 64]

# Celery
# http://docs.celeryproject.org/en/latest/configuration.html
BROKER_URL = env('CELERY_BROKER_URL')
CELERY_TASK_QUEUES = (
    Queue('default', Exchange('default'), routing_key='default'),
)
CELERY_TASK_DEFAULT_QUEUE = 'default'
CELERY_TASK_DEFAULT_EXCHANGE_TYPE = 'direct'
CELERY_TASK_DEFAULT_ROUTING_KEY = 'default'
CELERY_TASK_SERIALIZER = 'pickle'
CELERY_BEAT_SCHEDULE = {
    'clean-up-social-auth-cache': {
        'task': 'apps.social_auth_cache.tasks.clean_up_social_auth_cache',
        'schedule': timedelta(hours=1)
    }
}

# Social Auth
SOCIAL_AUTH_PIPELINE = [
    # Get the information we can about the user and return it in a simple
    # format to create the user instance later. On some cases the details are
    # already part of the auth response from the provider, but sometimes this
    # could hit a provider API.
    'social.pipeline.social_auth.social_details',

    # Get the social uid from whichever service we're authing thru. The uid is
    # the unique identifier of the given user in the provider.
    'social.pipeline.social_auth.social_uid',

    # Verifies that the current auth process is valid within the current
    # project, this is where emails and domains whitelists are applied (if
    # defined).
    'social.pipeline.social_auth.auth_allowed',

    # Checks if the current social-account is already associated in the site.
    'social.pipeline.social_auth.social_user',

    'apps.social_auth_cache.pipeline.cache_access_token',

    # Make up a username for this person and ensure it isn't taken.  If it is taken,
    # fail.
    'apps.users.pipeline.get_username',

    # Create a user account if we haven't found one yet.
    'social.pipeline.user.create_user',

    # Create the record that associated the social account with this user.
    'social.pipeline.social_auth.associate_user',

    # Populate the extra_data field in the social record with the values
    # specified by settings (and the default ones like access_token, etc).
    'social.pipeline.social_auth.load_extra_data',

    # Update the user record with any changed info from the auth service.
    'social.pipeline.user.user_details',

    'apps.users.pipeline.set_avatar',
    'apps.users.pipeline.set_is_new',
    'apps.referrals.pipeline.link_user_to_referrer',
]
SOCIAL_AUTH_USER_FIELDS = ['username', 'first_name', 'last_name']

## Social Auth Facebook
SOCIAL_AUTH_FACEBOOK_SCOPE = ['public_profile', 'email']
SOCIAL_AUTH_FACEBOOK_KEY = env('SOCIAL_AUTH_FACEBOOK_KEY', required=False)
SOCIAL_AUTH_FACEBOOK_SECRET = env('SOCIAL_AUTH_FACEBOOK_SECRET', required=False)
SOCIAL_AUTH_FACEBOOK_PROFILE_EXTRA_PARAMS = {
    'fields': 'id,email,first_name,last_name'
}
if SOCIAL_AUTH_FACEBOOK_KEY and SOCIAL_AUTH_FACEBOOK_SECRET:
    AUTHENTICATION_BACKENDS.append('social.backends.facebook.FacebookOAuth2')

## Social Auth Twitter
SOCIAL_AUTH_TWITTER_KEY = env('SOCIAL_AUTH_TWITTER_KEY', required=False)
SOCIAL_AUTH_TWITTER_SECRET = env('SOCIAL_AUTH_TWITTER_SECRET', required=False)
if SOCIAL_AUTH_TWITTER_KEY and SOCIAL_AUTH_TWITTER_SECRET:
    AUTHENTICATION_BACKENDS.append('social.backends.twitter.TwitterOAuth')

## Social Auth LinkedIn
SOCIAL_AUTH_LINKEDIN_OAUTH2_KEY = env('SOCIAL_AUTH_LINKEDIN_KEY', required=False)
SOCIAL_AUTH_LINKEDIN_OAUTH2_SECRET = env('SOCIAL_AUTH_LINKEDIN_SECRET', required=False)
SOCIAL_AUTH_LINKEDIN_OAUTH2_SCOPE = ['r_basicprofile', 'r_emailaddress']
SOCIAL_AUTH_LINKEDIN_OAUTH2_FIELD_SELECTORS = ['email-address', 'picture-urls::(original)']
if SOCIAL_AUTH_LINKEDIN_OAUTH2_KEY and SOCIAL_AUTH_LINKEDIN_OAUTH2_SECRET:
    AUTHENTICATION_BACKENDS.append('social.backends.linkedin.LinkedinOAuth2')

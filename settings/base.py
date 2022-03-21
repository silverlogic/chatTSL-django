"""
https://docs.djangoproject.com/en/1.9/ref/settings/
"""
import pathlib
from collections import OrderedDict
from datetime import timedelta

from django.utils.translation import gettext_lazy as _

import dj_database_url
from kombu import Exchange, Queue
from PIL import Image

from .env import env

BASE_DIR = pathlib.Path(__file__).parent.parent
SETTINGS_DIR = BASE_DIR / "settings"
APPS_DIR = BASE_DIR / "apps"
LOGS_DIR = BASE_DIR.parent / "logs"

ALLOWED_HOSTS = ["*"]  # Host checking done by web server.
ROOT_URLCONF = "apps.urls"
WSGI_APPLICATION = "apps.wsgi.application"

# Auth
AUTH_USER_MODEL = "users.User"
AUTHENTICATION_BACKENDS = ["django.contrib.auth.backends.ModelBackend"]
PASSWORD_HASHERS = ["django.contrib.auth.hashers.PBKDF2PasswordHasher"]

# Sites
DJANGO_ADMIN_HEADER = env("DJANGO_ADMIN_HEADER")
URL = env("URL")
FRONT_URL = env("FRONT_URL")
FRONT_CONFIRM_EMAIL_URL = FRONT_URL + "/confirm-email/{id}/{token}"
FRONT_FORGOT_PASSWORD_URL = FRONT_URL + "/forgot-password/{token}"
FRONT_CHANGE_EMAIL_CONFIRM_URL = FRONT_URL + "/change-email/{id}/{token}"
FRONT_CHANGE_EMAIL_VERIFY_URL = FRONT_URL + "/change-email-verify/{id}/{token}"

# IOS Deep Links
IOS_CONFIRM_EMAIL_DEEP_LINK = False
IOS_FORGOT_PASSWORD_DEEP_LINK = False
IOS_CHANGE_EMAIL_DEEP_LINK = False

# Android Deep Links
ANDROID_CONFIRM_EMAIL_DEEP_LINK = False
ANDROID_FORGOT_PASSWORD_DEEP_LINK = False
ANDROID_CHANGE_EMAIL_DEEP_LINK = False

# Mail
EMAIL_BACKEND = "djmail.backends.default.EmailBackend"
DJMAIL_MAX_RETRY_NUMBER = 3

INSTALLED_APPS = [
    "apps.base",
    # Django
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Third party
    "rest_framework",
    "rest_framework.authtoken",
    "djmail",
    "corsheaders",
    "avatar",
    "easy_thumbnails",
    "django_filters",
    "django_jinja",
    "crispy_forms",
    "social_django",
    "rest_social_auth",
    "fsm_admin",
    "phonenumber_field",
    "constance",
    "constance.backends.database",
    # Base
    "apps.api",
    "apps.referrals",
    "apps.social_auth_cache",
    "apps.users",
    # Project
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "apps.base.middleware.AdminTimezoneMiddleware",
]

TEMPLATES = [
    {
        "BACKEND": "django_jinja.backend.Jinja2",
        "DIRS": [str(APPS_DIR / "templates")],
        "APP_DIRS": True,
        "OPTIONS": {"match_extension": ".j2", "constants": {"URL": URL, "FRONT_URL": FRONT_URL}},
    },
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [str(APPS_DIR / "templates")],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ]
        },
    },
]

# Database
# https://docs.djangoproject.com/en/1.9/ref/settings/#databases
# https://github.com/kennethreitz/dj-database-url#url-schema
DATABASES = {}
DATABASES["default"] = dj_database_url.parse(env("DATABASE_URL"))

DEFAULT_AUTO_FIELD = "django.db.models.AutoField"

# Internationalization
# https://docs.djangoproject.com/en/1.9/topics/i18n/
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
ADMIN_TIME_ZONE = "US/Eastern"
USE_I18N = True
USE_L10N = True
USE_TZ = True
LANGUAGES = [("en", _("English"))]

DATA_UPLOAD_MAX_MEMORY_SIZE = None
DATA_UPLOAD_MAX_NUMBER_FIELDS = None

# For reverse proxying
USE_X_FORWARDED_HOST = True
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTOCOL", "https")

# Logging
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "root": {"handlers": ["console"], "level": "INFO"},
    "formatters": {
        "simple": {"format": "[%(name)s] [%(levelname)s] %(message)s"},
        "json": {"()": "apps.base.logging.BaseJSONFormatter"},
    },
    "handlers": {"console": {"class": "logging.StreamHandler", "formatter": "simple"},},
    "loggers": {},
}

LOGGING_FILE_HANDLERS = {
    "file_django": {
        "class": "logging.handlers.RotatingFileHandler",
        "formatter": "json",
        "filename": LOGS_DIR / "web.log",
        "maxBytes": 1024 * 1024 * 100,
        "backupCount": 2,
    },
    "file_celery": {
        "class": "logging.handlers.RotatingFileHandler",
        "formatter": "json",
        "filename": LOGS_DIR / "worker.log",
        "maxBytes": 1024 * 1024 * 100,
        "backupCount": 2,
    },
}

LOGGING_FILE_LOGGERS = {
    "django": {"handlers": ["file_django"], "level": "INFO",},
    "celery": {"handlers": ["file_celery"], "level": "INFO",},
}

LOGS_DIR_PRESENT = pathlib.Path(LOGS_DIR).exists()
LOGGING["handlers"].update(LOGGING_FILE_HANDLERS if LOGS_DIR_PRESENT else {})
LOGGING["loggers"] = LOGGING_FILE_LOGGERS if LOGS_DIR_PRESENT else {}
LOGGING["root"]["handlers"] = (
    LOGGING["root"]["handlers"] + ["file_django"]
    if LOGS_DIR_PRESENT
    else LOGGING["root"]["handlers"]
)


# Allow requests from any domain.
CORS_ORIGIN_ALLOW_ALL = True

# Rest Framework
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework.authentication.TokenAuthentication",
        "rest_framework.authentication.SessionAuthentication",
    ),
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 30,
    "DEFAULT_VERSIONING_CLASS": "rest_framework.versioning.NamespaceVersioning",
    "ORDERING_PARAM": "order_by",
    "SEARCH_PARAM": "q",
    "TEST_REQUEST_DEFAULT_FORMAT": "json",
}

# Avatars
AVATAR_GRAVATAR_DEFAULT = "mp"
AVATAR_STORAGE_DIR = "user-avatars"
AVATAR_HASH_USERDIRNAMES = True
AVATAR_EXPOSE_USERNAMES = False
AVATAR_HASH_FILENAMES = True
AVATAR_CLEANUP_DELETED = True
AVATAR_MAX_AVATARS_PER_USER = 1
AVATAR_AUTO_GENERATE_SIZES = [1024, 64]
AVATAR_CACHE_ENABLED = False
AVATAR_RESIZE_METHOD = Image.ANTIALIAS
AVATAR_THUMB_FORMAT = "PNG"
AVATAR_THUMB_QUALITY = 100

# Celery
# http://docs.celeryproject.org/en/latest/configuration.html
exchange_default = Exchange("default")
BROKER_URL = env("CELERY_BROKER_URL")
CELERY_TASK_QUEUES = (
    Queue("default", exchange_default, routing_key="default"),
    Queue("emails", exchange_default, routing_key="emails"),
)
CELERY_TASK_DEFAULT_QUEUE = "default"
CELERY_TASK_DEFAULT_EXCHANGE_TYPE = "direct"
CELERY_TASK_DEFAULT_ROUTING_KEY = "default"
CELERY_TASK_SERIALIZER = "json"
CELERY_TASK_ROUTES = {
    "djmail.tasks.send_messages": {"exchange": "default", "routing_key": "emails"},
    "djmail.tasks.retry_send_messages": {"exchange": "default", "routing_key": "emails"},
}
CELERY_BEAT_SCHEDULE = {
    "clean-up-social-auth-cache": {
        "task": "apps.social_auth_cache.tasks.clean_up_social_auth_cache",
        "schedule": timedelta(hours=1),
        "options": {"expires": 60 * 30},
    }
}

# Constance
CONSTANCE_BACKEND = "constance.backends.database.DatabaseBackend"
CONSTANCE_CONFIG = OrderedDict([])

# Social Auth
SOCIAL_AUTH_PIPELINE = [
    # Get the information we can about the user and return it in a simple
    # format to create the user instance later. On some cases the details are
    # already part of the auth response from the provider, but sometimes this
    # could hit a provider API.
    "social_core.pipeline.social_auth.social_details",
    # Get the social uid from whichever service we're authing thru. The uid is
    # the unique identifier of the given user in the provider.
    "social_core.pipeline.social_auth.social_uid",
    # Verifies that the current auth process is valid within the current
    # project, this is where emails and domains whitelists are applied (if
    # defined).
    "social_core.pipeline.social_auth.auth_allowed",
    # Checks if the current social-account is already associated in the site.
    "social_core.pipeline.social_auth.social_user",
    "apps.social_auth_cache.pipeline.cache_access_token",
    # Make up a username for this person and ensure it isn't taken.  If it is taken,
    # fail.
    "apps.users.pipeline.get_username",
    # Create a user account if we haven't found one yet.
    "social_core.pipeline.user.create_user",
    # Create the record that associated the social account with this user.
    "social_core.pipeline.social_auth.associate_user",
    # Populate the extra_data field in the social record with the values
    # specified by settings (and the default ones like access_token, etc).
    "social_core.pipeline.social_auth.load_extra_data",
    # Update the user record with any changed info from the auth service.
    "social_core.pipeline.user.user_details",
    "apps.users.pipeline.set_avatar",
    "apps.users.pipeline.set_is_new",
    "apps.referrals.pipeline.link_user_to_referrer",
]
SOCIAL_AUTH_USER_FIELDS = ["username", "first_name", "last_name"]

## Social Auth Facebook
SOCIAL_AUTH_FACEBOOK_SCOPE = ["public_profile", "email"]
SOCIAL_AUTH_FACEBOOK_KEY = env("SOCIAL_AUTH_FACEBOOK_KEY", required=False)
SOCIAL_AUTH_FACEBOOK_SECRET = env("SOCIAL_AUTH_FACEBOOK_SECRET", required=False)
SOCIAL_AUTH_FACEBOOK_PROFILE_EXTRA_PARAMS = {"fields": "id,email,first_name,last_name"}
if SOCIAL_AUTH_FACEBOOK_KEY and SOCIAL_AUTH_FACEBOOK_SECRET:
    AUTHENTICATION_BACKENDS.append("social_core.backends.facebook.FacebookOAuth2")

## Social Auth Twitter
SOCIAL_AUTH_TWITTER_KEY = env("SOCIAL_AUTH_TWITTER_KEY", required=False)
SOCIAL_AUTH_TWITTER_SECRET = env("SOCIAL_AUTH_TWITTER_SECRET", required=False)
if SOCIAL_AUTH_TWITTER_KEY and SOCIAL_AUTH_TWITTER_SECRET:
    AUTHENTICATION_BACKENDS.append("social_core.backends.twitter.TwitterOAuth")

## Social Auth LinkedIn
SOCIAL_AUTH_LINKEDIN_OAUTH2_KEY = env("SOCIAL_AUTH_LINKEDIN_KEY", required=False)
SOCIAL_AUTH_LINKEDIN_OAUTH2_SECRET = env("SOCIAL_AUTH_LINKEDIN_SECRET", required=False)
SOCIAL_AUTH_LINKEDIN_OAUTH2_SCOPE = ["r_basicprofile", "r_emailaddress"]
SOCIAL_AUTH_LINKEDIN_OAUTH2_FIELD_SELECTORS = ["email-address", "picture-urls::(original)"]
if SOCIAL_AUTH_LINKEDIN_OAUTH2_KEY and SOCIAL_AUTH_LINKEDIN_OAUTH2_SECRET:
    AUTHENTICATION_BACKENDS.append("social_core.backends.linkedin.LinkedinOAuth2")

# Phone Numbers
PHONENUMBER_DB_FORMAT = "E164"

# BRANCH.IO
BRANCHIO_KEY = env("BRANCHIO_KEY")

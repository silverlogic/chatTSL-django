import logging

import sentry_sdk
from sentry_sdk.integrations.celery import CeleryIntegration
from sentry_sdk.integrations.django import DjangoIntegration
from sentry_sdk.integrations.logging import LoggingIntegration

from apps.sentry import fetch_git_sha

from .base import *  # noqa

DEBUG = False
SECRET_KEY = env("SECRET_KEY")

# Email
DEFAULT_FROM_EMAIL = env("DEFAULT_FROM_EMAIL")
EMAIL_BACKEND = "djmail.backends.celery.EmailBackend"
DJMAIL_REAL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = env("EMAIL_HOST")
EMAIL_HOST_USER = env("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = env("EMAIL_HOST_PASSWORD")
EMAIL_PORT = env("EMAIL_PORT")
EMAIL_USE_TLS = env("EMAIL_USE_TLS")

# AWS
AWS_ACCESS_KEY_ID = env("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = env("AWS_SECRET_ACCESS_KEY")
AWS_QUERYSTRING_AUTH = False

# Static / Media Files
AWS_STORAGE_BUCKET_NAME = env("AWS_STORAGE_BUCKET_NAME")
STATICFILES_STORAGE = "s3_folder_storage.s3.StaticStorage"
STATIC_S3_PATH = "static"
STATIC_URL = "https://{}.s3.amazonaws.com/{}/".format(AWS_STORAGE_BUCKET_NAME, STATIC_S3_PATH)
DEFAULT_FILE_STORAGE = "s3_folder_storage.s3.DefaultStorage"
DEFAULT_S3_PATH = "media"
MEDIA_URL = "https://{}.s3.amazonaws.com/{}/".format(AWS_STORAGE_BUCKET_NAME, DEFAULT_S3_PATH)
INSTALLED_APPS += ["storages", "s3_folder_storage"]

# Thumbnails
THUMBNAIL_DEFAULT_STORAGE = DEFAULT_FILE_STORAGE

# Environment
ENVIRONMENT = env("SENTRY_ENVIRONMENT")

# Sentry
SENTRY_DSN = env("SENTRY_DSN")
SENTRY_LOG_LEVEL = logging.INFO
sentry_logging = LoggingIntegration(level=SENTRY_LOG_LEVEL, event_level=logging.ERROR)
SENTRY_RELEASE = fetch_git_sha(BASE_DIR)
sentry_sdk.init(
    dsn=SENTRY_DSN,
    integrations=[sentry_logging, DjangoIntegration(), CeleryIntegration()],
    release=SENTRY_RELEASE,
    send_default_pii=True,
)

# Channels
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {"hosts": [env("REDIS_URL")]},
    },
}

from .base import *  # noqa

DEBUG = False
SECRET_KEY = env('SECRET_KEY')

# Email
DEFAULT_FROM_EMAIL = env('DEFAULT_FROM_EMAIL')
EMAIL_BACKEND = 'djmail.backends.celery.EmailBackend'
DJMAIL_REAL_BACKEND = 'django_ses.SESBackend'

# AWS
AWS_ACCESS_KEY_ID = env('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = env('AWS_SECRET_ACCESS_KEY')

# Static / Media Files
AWS_STORAGE_BUCKET_NAME = env('AWS_STORAGE_BUCKET_NAME')
STATICFILES_STORAGE = 's3_folder_storage.s3.StaticStorage'
STATIC_S3_PATH = 'static'
STATIC_URL = 'https://{}.s3.amazonaws.com/{}/'.format(AWS_STORAGE_BUCKET_NAME, STATIC_S3_PATH)
DEFAULT_FILE_STORAGE = 's3_folder_storage.s3.DefaultStorage'
DEFAULT_S3_PATH = 'media'
MEDIA_URL = 'https://{}.s3.amazonaws.com/{}/' % AWS_STORAGE_BUCKET_NAME

# Sentry (raven) error logging
INSTALLED_APPS += ['raven.contrib.django.raven_compat']
RAVEN_CONFIG = {
    'dsn': env('SENTRY_DSN')
}
LOGGING['handlers']['sentry'] = {
    'level': 'ERROR',
    'class': 'raven.contrib.django.handlers.SentryHandler',
}
LOGGING['root']['handlers'].append('sentry')

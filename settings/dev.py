from .base import *  # noqa

DEBUG = True
SECRET_KEY = '1234'

# Email
DEFAULT_FROM_EMAIL = 'john@test.com'
DJMAIL_REAL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Must be absolute URLs for use in emails.
MEDIA_ROOT = BASE_DIR.parent / 'media'
MEDIA_URL = 'http://localhost:8000/media/'
STATIC_ROOT = BASE_DIR.parent / 'static'
STATIC_URL = 'http://localhost:8000/static/'

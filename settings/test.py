from .dev import *  # noqa

DEFAULT_FILE_STORAGE = 'inmemorystorage.InMemoryStorage'
INMEMORYSTORAGE_PERSIST = True

# Emails
DJMAIL_REAL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'

# Debug Toolbar
INSTALLED_APPS.remove('debug_toolbar')
MIDDLEWARE.remove('debug_toolbar.middleware.DebugToolbarMiddleware')

# Silk
INSTALLED_APPS.remove('silk')
MIDDLEWARE.remove('silk.middleware.SilkyMiddleware')

# Speeds up tests.
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
]

# Celery
CELERY_TASK_ALWAYS_EAGER = True

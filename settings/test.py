from .dev import *  # noqa

DEFAULT_FILE_STORAGE = 'inmemorystorage.InMemoryStorage'
INMEMORYSTORAGE_PERSIST = True

# Emails
DJMAIL_REAL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'

# Speeds up tests.
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
]

# Celery
CELERY_TASK_ALWAYS_EAGER = True

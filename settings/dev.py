from .base import *  # noqa

DEBUG = True
SECRET_KEY = '1234'

# Email
DEFAULT_FROM_EMAIL = 'john@test.com'
DJMAIL_REAL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Must be absolute URLs for use in emails.
DEFAULT_FILE_STORAGE = 'inmemorystorage.InMemoryStorage'
INMEMORYSTORAGE_PERSIST = True
MEDIA_ROOT = str(BASE_DIR.parent / 'media')
MEDIA_URL = '{url}/media/'.format(url=URL)
STATIC_ROOT = str(BASE_DIR.parent / 'static')
STATIC_URL = '{url}/static/'.format(url=URL)

# Debug Toolbar
INSTALLED_APPS += ['debug_toolbar']
MIDDLEWARE = ['debug_toolbar.middleware.DebugToolbarMiddleware'] + MIDDLEWARE
DEBUG_TOOLBAR_CONFIG = {
    'SHOW_TOOLBAR_CALLBACK': 'apps.base.debug_toolbar.show_toolbar'
}

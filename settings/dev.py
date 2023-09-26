from .base import *  # noqa

DEBUG = True
SECRET_KEY = "1234"

# Email
DEFAULT_FROM_EMAIL = "john@test.com"
DJMAIL_REAL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# Must be absolute URLs for use in emails.
MEDIA_ROOT = str(BASE_DIR.parent / "media")
MEDIA_URL = "{url}/media/".format(url=URL)
STATIC_ROOT = str(BASE_DIR.parent / "static")
STATIC_URL = "{url}/static/".format(url=URL)

# Debug Toolbar
INSTALLED_APPS += ["debug_toolbar"]
MIDDLEWARE = ["debug_toolbar.middleware.DebugToolbarMiddleware"] + MIDDLEWARE
DEBUG_TOOLBAR_CONFIG = {
    "SHOW_TOOLBAR_CALLBACK": "apps.base.debug_toolbar.show_toolbar",
    "DISABLE_PANELS": [  # These panels slow down the app
        "debug_toolbar.panels.sql.SQLPanel",
        "debug_toolbar.panels.cache.CachePanel",
        "debug_toolbar.panels.signals.SignalsPanel",
        "debug_toolbar.panels.logging.LoggingPanel",
        "debug_toolbar.panels.profiling.ProfilingPanel",
        "debug_toolbar.panels.redirects.RedirectsPanel",
    ],
}

# Environment
ENVIRONMENT = "development"

# Silk
INSTALLED_APPS += ["silk", "django_extensions"]
MIDDLEWARE = ["silk.middleware.SilkyMiddleware"] + MIDDLEWARE
SILKY_PYTHON_PROFILER = True
SILKY_PYTHON_PROFILER_BINARY = True
SILKY_META = True

# Channels
CHANNEL_LAYERS = {"default": {"BACKEND": "channels.layers.InMemoryChannelLayer"}}

# Cache
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
    }
}

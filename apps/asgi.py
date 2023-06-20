"""

isort:skip_file

"""

from django.core.asgi import get_asgi_application

from channels.routing import ProtocolTypeRouter

from channels.routing import URLRouter

from apps.api.channels import TokenAuthMiddleware  # noqa
from apps.api.ws.urls import websocket_urlpatterns  # noqa

django_asgi_app = get_asgi_application()
application = ProtocolTypeRouter(
    {"http": django_asgi_app, "websocket": TokenAuthMiddleware(URLRouter(websocket_urlpatterns))}
)

from django.conf import settings  # noqa

if settings.ENVIRONMENT in ["production", "staging"]:
    from sentry_sdk.integrations.asgi import SentryAsgiMiddleware

    application = SentryAsgiMiddleware(application)

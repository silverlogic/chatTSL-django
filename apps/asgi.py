"""

isort:skip_file

"""

from django.core.asgi import get_asgi_application
from django.urls import re_path

from channels.routing import ProtocolTypeRouter

from channels.routing import URLRouter
from apps.api.channels import TokenAuthMiddleware

django_asgi_app = get_asgi_application()

# we need to load all applications before we can import from the apps

from apps.api.v1.users.channels import UsersConsumer  # noqa


application = ProtocolTypeRouter(
    {
        "http": django_asgi_app,
        "websocket": TokenAuthMiddleware(
            URLRouter(
                [
                    re_path(r"ws/users/$", UsersConsumer.as_asgi()),
                ]
            )
        ),
    }
)

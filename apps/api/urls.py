from django.conf.urls import include, re_path

from .v1.router import router as v1_router
from .ws.urls import websocket_urlpatterns  # noqa

urlpatterns = [
    re_path(r"v1/", include((v1_router.urls, "v1"), namespace="v1")),
    re_path(r"", include((websocket_urlpatterns, ""), namespace="")),
]

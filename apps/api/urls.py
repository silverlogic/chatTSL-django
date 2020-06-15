from django.conf.urls import include, url

from .v1.router import router as v1_router

urlpatterns = [url(r"v1/", include((v1_router.urls, "v1"), namespace="v1"))]

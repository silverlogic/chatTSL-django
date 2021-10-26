from django.conf.urls import include, re_path

from .v1.router import router as v1_router

urlpatterns = [re_path(r"v1/", include((v1_router.urls, "v1"), namespace="v1"))]

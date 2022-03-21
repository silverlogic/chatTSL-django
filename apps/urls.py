from django.apps import apps
from django.conf import settings
from django.conf.urls import include, re_path
from django.contrib import admin

urlpatterns = [
    re_path(r"", include("apps.api.urls")),
    re_path(r"^api-auth/", include("rest_framework.urls", namespace="rest_framework")),
    re_path(r"^avatar/", include("avatar.urls")),
    re_path(r"^admin/", admin.site.urls),
]


if settings.ENVIRONMENT in ["staging"]:
    admin.site.site_header = "Django administration staging"


if settings.ENVIRONMENT in ["development"]:
    admin.site.site_header = "Django administration development"


if settings.ENVIRONMENT in ["development"]:
    admin.site.site_header = "Django administration production"


if settings.DEBUG:
    import debug_toolbar
    from django.conf.urls.static import static
    from urllib.parse import urlparse

    media_url = urlparse(settings.MEDIA_URL)
    static_url = urlparse(settings.STATIC_URL)
    urlpatterns += static(media_url.path, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(static_url.path, document_root=settings.STATIC_ROOT)
    urlpatterns += [re_path(r"^__debug__/", include(debug_toolbar.urls))]


if apps.is_installed("silk"):
    urlpatterns += [re_path(r"^silk/", include("silk.urls", namespace="silk"))]

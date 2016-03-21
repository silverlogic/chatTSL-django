from django.conf import settings
from django.conf.urls import include, url
from django.contrib import admin

urlpatterns = [
    url(r'', include('apps.api.urls')),
    url(r'^admin/', admin.site.urls),
]


if settings.DEBUG:
    from django.conf.urls.static import static
    from urllib.parse import urlparse
    media_url = urlparse(settings.MEDIA_URL)
    static_url = urlparse(settings.STATIC_URL)
    urlpatterns += static(media_url.path, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(static_url.path, document_root=settings.STATIC_ROOT)

from django.apps import apps
from django.conf import settings
from django.conf.urls import include, url
from django.contrib import admin

urlpatterns = [
    url(r'', include('apps.api.urls')),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^avatar/', include('avatar.urls')),
    url(r'^admin/', admin.site.urls),
]


if settings.DEBUG:
    import debug_toolbar
    from django.conf.urls.static import static
    from urllib.parse import urlparse
    media_url = urlparse(settings.MEDIA_URL)
    static_url = urlparse(settings.STATIC_URL)
    urlpatterns += static(media_url.path, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(static_url.path, document_root=settings.STATIC_ROOT)
    urlpatterns += [url(r'^__debug__/', include(debug_toolbar.urls))]


if apps.is_installed('silk'):
    urlpatterns += [url(r'^silk/', include('silk.urls', namespace='silk'))]

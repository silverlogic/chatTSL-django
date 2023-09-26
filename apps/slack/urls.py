from django.urls import path

from . import views

urlpatterns = [
    path("event/hook/", views.event_hook, name="event_hook"),
    path("slash/chat-settings/", views.slash_chat_settings, name="slash_chat_settings"),
    path("interactive-endpoint/", views.interactive_endpoint, name="slash_new_chat"),
]

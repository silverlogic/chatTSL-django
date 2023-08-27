from django.urls import path

from . import views

urlpatterns = [
    path("event/hook/", views.event_hook, name="event_hook"),
    path("slash/new-chat/", views.slash_new_chat, name="slash_new_chat"),
]

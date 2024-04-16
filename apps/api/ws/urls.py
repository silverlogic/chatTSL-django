from django.urls import re_path

from apps.api.v1.users.channels import UsersConsumer  # noqa
from apps.api.ws.chatbot.consumers import OpenAIChatConsumer  # noqa

websocket_urlpatterns = [
    re_path(r"ws/users/$", UsersConsumer.as_asgi(), name="ws-users"),
    re_path(r"ws/chat/(?P<chat_id>\w+)/$", OpenAIChatConsumer.as_asgi(), name="ws-chat"),
]

from django.shortcuts import get_object_or_404

from rest_framework import mixins, permissions, response, status, viewsets

from apps.api.mixins import DestroyModelMixin
from apps.chatbot.models import OpenAIChat, OpenAIChatMessage

from .serializers import (
    OpenAIChatMessageSerializer,
    OpenAIChatMessageUpdateSerializer,
    OpenAIChatSerializer,
)


class OpenAIChatViewSet(
    viewsets.GenericViewSet,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    DestroyModelMixin,
):
    serializer_class = OpenAIChatSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = OpenAIChat.objects.all()

    def get_queryset(self):
        return super().get_queryset().filter(user=self.request.user)


class OpenAIChatMessageViewSet(
    viewsets.GenericViewSet,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    DestroyModelMixin,
    mixins.UpdateModelMixin,
):
    @property
    def serializer_class(self):
        if self.request.method in ["PATCH", "PUT"]:
            return OpenAIChatMessageUpdateSerializer
        else:
            return OpenAIChatMessageSerializer

    permission_classes = [permissions.IsAuthenticated]
    queryset = OpenAIChatMessage.objects.all()

    def get_queryset(self):
        return super().get_queryset().filter(chat__user=self.request.user)

    def create(self, request, *args, **kwargs):
        data = request.data
        chat_id = data.pop("chat", -1)
        chat = get_object_or_404(OpenAIChat.objects.all(), id=chat_id, user=request.user)
        self.check_object_permissions(request, chat)
        serializer = self.get_serializer(data=dict(**data, chat=chat.id))
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return response.Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

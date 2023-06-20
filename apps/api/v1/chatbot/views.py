from rest_framework import mixins, permissions, viewsets

from apps.chatbot.models import OpenAIChat

from .serializers import OpenAIChatSerializer


class OpenAIChatViewSet(
    viewsets.GenericViewSet,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    mixins.DestroyModelMixin,
):
    serializer_class = OpenAIChatSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = OpenAIChat.objects.all()

    def get_queryset(self):
        return super().get_queryset().filter(user=self.request.user)

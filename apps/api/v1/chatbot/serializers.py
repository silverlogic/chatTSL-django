from __future__ import annotations

from rest_framework import serializers

from apps.chatbot.models import OpenAIChat, OpenAIChatMessage


class OpenAIChatSerializer(serializers.ModelSerializer):
    messages: OpenAIChatMessageSerializer

    class Meta:
        model = OpenAIChat
        fields = ["id", "user", "model", "messages"]
        read_only_fields = ("user", "messages")

    def __new__(cls, *args, **kwargs):
        cls._declared_fields["messages"] = OpenAIChatMessageSerializer(many=True, read_only=True)
        return super().__new__(cls, *args, **kwargs)

    def create(self, validated_data):
        user: None
        request = self.context.get("request", None)
        scope = self.context.get("scope", None)
        if request:
            user = request.user
        if scope:
            user = scope.get("user", None)
        validated_data["user"] = user
        return super().create(validated_data)


class OpenAIChatMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = OpenAIChatMessage
        fields = ["id", "chat", "role", "content"]

from __future__ import annotations

from rest_framework import serializers

from apps.api.v1.tettra.serializers import TettraPageSerializer
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
    tettra_pages: TettraPageSimpleSerializer

    def __new__(cls, *args, **kwargs):
        cls._declared_fields["tettra_pages"] = TettraPageSimpleSerializer(many=True, read_only=True)
        return super().__new__(cls, *args, **kwargs)

    class Meta:
        model = OpenAIChatMessage
        fields = ["id", "chat", "role", "content", "tettra_pages"]


class TettraPageSimpleSerializer(TettraPageSerializer):
    class Meta(TettraPageSerializer.Meta):
        fields = (
            "id",
            "page_id",
            "page_title",
            "owner_id",
            "owner_name",
            "owner_email",
            "url",
            "category_id",
            "category_name",
            "subcategory_id",
            "subcategory_name",
        )

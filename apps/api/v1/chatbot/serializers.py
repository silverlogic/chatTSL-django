from __future__ import annotations

from collections import OrderedDict

from rest_framework import serializers

from apps.api.v1.tettra.serializers import (
    TettraPageCategorySerializer,
    TettraPageSerializer,
    TettraPageSubcategorySerializer,
)
from apps.chatbot.models import OpenAIChat, OpenAIChatMessage


class OpenAIChatSerializer(serializers.ModelSerializer):
    messages: OpenAIChatMessageSerializer
    tettra_page_category_filter = TettraPageCategorySerializer(many=False, default=None)
    tettra_page_subcategory_filter = TettraPageSubcategorySerializer(many=False, default=None)

    class Meta:
        model = OpenAIChat
        fields = [
            "id",
            "user",
            "model",
            "messages",
            "tettra_page_category_filter",
            "tettra_page_subcategory_filter",
        ]
        read_only_fields = ["id", "user", "messages"]

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


class OpenAIChatUpdateSerializer(serializers.ModelSerializer):
    def __new__(cls, *args, **kwargs):
        cls._declared_fields["messages"] = OpenAIChatMessageSerializer(many=True, read_only=True)
        return super().__new__(cls, *args, **kwargs)

    class Meta(OpenAIChatSerializer.Meta):
        read_only_fields = ["id", "user", "messages"]


class OpenAIChatMessageSerializer(serializers.ModelSerializer):
    tettra_pages = serializers.SerializerMethodField()

    class Meta:
        model = OpenAIChatMessage
        fields = ["id", "chat", "role", "content", "tettra_pages", "rating"]

    def get_tettra_pages(self, instance):
        tettra_pages = OrderedDict()
        for tettra_page_chunk in instance.tettra_page_chunks.all():
            tettra_pages[tettra_page_chunk.tettra_page.id] = tettra_page_chunk.tettra_page
        return TettraPageSimpleSerializer(
            list(tettra_pages.values()), many=True, read_only=True
        ).data


class OpenAIChatMessageUpdateSerializer(OpenAIChatMessageSerializer):
    class Meta(OpenAIChatMessageSerializer.Meta):
        read_only_fields = ["id", "chat", "role", "content", "tettra_pages"]


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
            "category",
            "subcategory",
        )

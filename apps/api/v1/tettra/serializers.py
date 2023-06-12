from rest_framework import serializers

from apps.tettra.models import TettraPage


class TettraPageImportDumpSerializer(serializers.Serializer):
    file = serializers.FileField()

    class Meta:
        fields = ("file",)


class TettraPageSerializer(serializers.ModelSerializer):
    class Meta:
        model = TettraPage
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
            "html",
        )

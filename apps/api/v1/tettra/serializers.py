from django.db import transaction

from rest_framework import serializers

from apps.tettra.models import TettraPage, TettraPageCategory, TettraPageSubcategory


class TettraPageImportDumpSerializer(serializers.Serializer):
    file = serializers.FileField()

    class Meta:
        fields = ("file",)


class TettraPageSerializer(serializers.ModelSerializer):
    def __new__(cls, *args, **kwargs):
        cls._declared_fields["category"] = TettraPageCategorySerializer(many=False)
        cls._declared_fields["subcategory"] = TettraPageSubcategorySerializer(many=False)
        return super().__new__(cls, *args, **kwargs)

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
            "category",
            "subcategory",
            "html",
        )

    @transaction.atomic
    def create(self, validated_data):
        category_data = validated_data.pop("category")
        category = TettraPageCategory.objects.filter(
            category_id=category_data.get("category_id")
        ).first()

        subcategory_data = validated_data.pop("subcategory", None)
        subcategory: TettraPageSubcategory = None

        category_serializer = self.fields["category"].__class__(
            instance=category, data=category_data
        )
        category_serializer.is_valid(raise_exception=True)
        category = category_serializer.save()
        validated_data["category"] = category

        if isinstance(subcategory_data, dict):
            subcategory = TettraPageSubcategory.objects.filter(
                subcategory_id=subcategory_data.get("subcategory_id")
            ).first()
            subcategory_serializer = self.fields["subcategory"].__class__(
                instance=subcategory, data=subcategory_data
            )
            subcategory_serializer.is_valid(raise_exception=True)
            subcategory = subcategory_serializer.save()
        validated_data["subcategory"] = subcategory

        return super().create(validated_data=validated_data)

    @transaction.atomic
    def update(self, instance, validated_data):
        category_data = validated_data.pop("category")
        category = TettraPageCategory.objects.filter(
            category_id=category_data.get("category_id")
        ).first()

        subcategory_data = validated_data.pop("subcategory", None)
        subcategory: TettraPageSubcategory = None

        category_serializer = self.fields["category"].__class__(
            instance=category, data=category_data
        )
        category_serializer.is_valid(raise_exception=True)
        category = category_serializer.save()
        validated_data["category"] = category

        if isinstance(subcategory_data, dict):
            subcategory = TettraPageSubcategory.objects.filter(
                subcategory_id=subcategory_data.get("subcategory_id")
            ).first()
            subcategory_serializer = self.fields["subcategory"].__class__(
                instance=subcategory, data=subcategory_data
            )
            subcategory_serializer.is_valid(raise_exception=True)
            subcategory = subcategory_serializer.save()
        validated_data["subcategory"] = subcategory

        return super().update(instance=instance, validated_data=validated_data)


class TettraPageCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = TettraPageCategory
        fields = (
            "id",
            "category_id",
            "category_name",
        )


class TettraPageSubcategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = TettraPageSubcategory
        fields = (
            "id",
            "subcategory_id",
            "subcategory_name",
            "subcategory_icon",
        )

from django.contrib import admin
from django.db.models import BooleanField, Count, ExpressionWrapper, Q

from .models import TettraPage, TettraPageCategory, TettraPageChunk, TettraPageSubcategory


@admin.register(TettraPage)
class TettraPageAdmin(admin.ModelAdmin):
    @admin.action(description="Refresh Embeddings")
    def refresh_embeddings(modeladmin, request, queryset):
        for instance in queryset:
            instance.chunks.all().delete()
            instance.save()

    list_display = ("id", "page_id", "page_title", "url", "chunk_count")
    search_fields = ("page_title", "category__category_name", "subcategory__subcategory_name")
    list_filter = ["category__category_name", "subcategory__subcategory_name"]
    actions = [refresh_embeddings]

    def get_queryset(self, request):
        return super().get_queryset(request=request).annotate(chunk_count=Count("chunks"))

    def chunk_count(self, obj):
        return obj.chunk_count


@admin.register(TettraPageCategory)
class TettraPageCategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "category_id", "category_name")


@admin.register(TettraPageSubcategory)
class TettraPageSubcategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "subcategory_id", "subcategory_name")


@admin.register(TettraPageChunk)
class TettraPageChunkAdmin(admin.ModelAdmin):
    list_display = ("id", "tettra_page", "content", "has_embedding")
    readonly_fields = ("embedding",)
    search_fields = (
        "content",
        "tettra_page__page_title",
        "tettra_page__category__category_name",
        "tettra_page__subcategory__subcategory_name",
    )

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request=request)
            .annotate(
                has_embedding=ExpressionWrapper(
                    Q(embedding__isnull=False), output_field=BooleanField()
                )
            )
        )

    def has_embedding(self, obj):
        return obj.has_embedding

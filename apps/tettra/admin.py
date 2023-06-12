from django.contrib import admin
from django.db.models import BooleanField, ExpressionWrapper, Q

from .models import TettraPage


@admin.register(TettraPage)
class TettraPageAdmin(admin.ModelAdmin):
    list_display = ("id", "page_id", "page_title", "url", "has_embedding")
    readonly_fields = ("embedding",)

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request=request)
            .annotate(
                has_embedding=ExpressionWrapper(
                    Q(embedding__isnull=True), output_field=BooleanField()
                )
            )
        )

    def has_embedding(self, obj):
        return obj.has_embedding

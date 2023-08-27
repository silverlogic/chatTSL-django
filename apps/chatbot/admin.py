from django.contrib import admin

from .models import OpenAIChat, OpenAIChatMessage


@admin.register(OpenAIChat)
class OpenAIChatAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "model", "created")
    sortable_by = ("created",)


@admin.register(OpenAIChatMessage)
class OpenAIChatMessageAdmin(admin.ModelAdmin):
    list_display = ("id", "chat", "role", "content", "rating", "created")
    list_filter = ("rating",)
    filter_horizontal = ("tettra_page_chunks",)
    sortable_by = ("created",)
    search_fields = ("content",)

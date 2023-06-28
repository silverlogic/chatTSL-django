from django.contrib import admin

from .models import OpenAIChat, OpenAIChatMessage


@admin.register(OpenAIChat)
class OpenAIChatAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "model")


@admin.register(OpenAIChatMessage)
class OpenAIChatMessageAdmin(admin.ModelAdmin):
    list_display = ("id", "chat", "role", "content")
    filter_horizontal = ("tettra_pages",)

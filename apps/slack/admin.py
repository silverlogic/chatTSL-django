import json

from django.contrib import admin
from django.utils.html import format_html

from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import JsonLexer

from .models import SlackEventCallbackData, SlackInstallation, SlackOpenAIChat


@admin.register(SlackInstallation)
class SlackInstallationAdmin(admin.ModelAdmin):
    list_display = ("id",)
    fields = ("slack_oauth_response_pretty",)
    readonly_fields = ("slack_oauth_response_pretty",)

    def slack_oauth_response_pretty(self, instance):
        if instance.slack_oauth_response is None:
            return None
        return format_html(
            highlight("{}", JsonLexer(), HtmlFormatter()),
            json.dumps(instance.slack_oauth_response, sort_keys=True, indent=2),
        )

    slack_oauth_response_pretty.short_description = "slack_oauth_response"


@admin.register(SlackEventCallbackData)
class SlackEventCallbackDataAdmin(admin.ModelAdmin):
    list_display = ("id",)
    fields = ("data_pretty",)
    readonly_fields = ("data_pretty",)

    def data_pretty(self, instance):
        return format_html(
            highlight("{}", JsonLexer(), HtmlFormatter()),
            json.dumps(instance.data, sort_keys=True, indent=2),
        )

    data_pretty.short_description = "data"


@admin.register(SlackOpenAIChat)
class SlackOpenAIChatAdmin(admin.ModelAdmin):
    list_display = ("id", "chat", "celery_task_id")
    fields = ("chat", "slack_event_json_pretty")
    readonly_fields = (
        "chat",
        "slack_event_json_pretty",
        "celery_task_id",
    )

    def slack_event_json_pretty(self, instance):
        if instance.slack_event_json is None:
            return None
        return format_html(
            highlight("{}", JsonLexer(), HtmlFormatter()),
            json.dumps(instance.slack_event_json, sort_keys=True, indent=2),
        )

    slack_event_json_pretty.short_description = "slack_event_json"

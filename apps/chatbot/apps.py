from django.apps import AppConfig


class SlackConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.chatbot"

    def ready(self):
        from . import signals  # noqa

from django.apps import AppConfig


class ChatbotAppConfig(AppConfig):
    name = "apps.chatbot"

    def ready(self):
        import apps.chatbot.signals  # noqa: F401

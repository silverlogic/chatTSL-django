from django.apps import AppConfig


class TettraConfig(AppConfig):
    name = "apps.tettra"

    def ready(self):
        from . import signals  # noqa

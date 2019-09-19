from django.conf import settings

import celery


class Celery(celery.Celery):
    def on_configure(self):
        if hasattr(settings, "RAVEN_CONFIG") and settings.RAVEN_CONFIG["dsn"]:
            import raven
            from raven.contrib.celery import register_signal, register_logger_signal

            client = raven.Client(settings.RAVEN_CONFIG["dsn"])
            register_logger_signal(client)
            register_signal(client)


app = Celery("apps")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()

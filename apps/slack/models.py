from django.db import models

from celery.result import AsyncResult
from model_utils.models import TimeStampedModel


class SlackInstallation(TimeStampedModel):
    slack_oauth_response = models.JSONField(null=False, blank=False, default=None)


class SlackEventCallbackData(TimeStampedModel):
    data = models.JSONField(null=False, blank=False, default=None)


class SlackOpenAIChat(TimeStampedModel):
    celery_task_id = models.UUIDField(null=True, blank=True)
    chat = models.OneToOneField(
        "chatbot.OpenAIChat",
        related_name="slack_chat",
        null=False,
        blank=False,
        on_delete=models.CASCADE,
    )
    slack_event_json = models.JSONField(null=False, blank=False, default=None)

    @property
    def is_celery_task_processing(self) -> bool:
        if not self.celery_task_id:
            return False
        result = AsyncResult(id=self.celery_task_id)
        return not result.ready()

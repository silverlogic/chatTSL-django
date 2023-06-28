from typing import Type

from django.db import models
from django.utils.translation import ugettext as _

from langchain.schema import AIMessage, BaseMessage, HumanMessage, SystemMessage
from model_utils import Choices


class OpenAIChat(models.Model):
    MODELS = Choices(
        "gpt-4",
        "gpt-3.5-turbo-16k",
        "gpt-3.5-turbo",
        "gpt-4-0613",
        "gpt-4-0314",
    )

    user = models.ForeignKey("users.User", related_name="chat", on_delete=models.CASCADE)
    model = models.CharField(
        null=False, blank=False, max_length=20, choices=MODELS, default=MODELS["gpt-4"]
    )


class OpenAIChatMessage(models.Model):
    ROLES = Choices(
        ("system", _("system")),
        ("user", _("user")),
        ("assistant", _("assistant")),
    )
    MAX_TETTRA_PAGES = 3

    chat = models.ForeignKey(OpenAIChat, related_name="messages", on_delete=models.CASCADE)
    role = models.CharField(null=False, blank=False, max_length=9, choices=ROLES)
    content = models.TextField(null=False, blank=False)
    tettra_pages = models.ManyToManyField(
        "tettra.TettraPage",
        related_name="tettra_pages",
        help_text=_("Similar tettra pages to the content of this message."),
        blank=True,
    )

    @property
    def LangchainSchemaMessageClass(self) -> Type[BaseMessage]:
        if self.role == self.__class__.ROLES.system:
            return SystemMessage
        if self.role == self.__class__.ROLES.user:
            return HumanMessage
        if self.role == self.__class__.ROLES.assistant:
            return AIMessage

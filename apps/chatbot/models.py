from typing import Type

from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _

from langchain.schema import AIMessage, BaseMessage, HumanMessage, SystemMessage
from model_utils import Choices
from model_utils.models import TimeStampedModel


class OpenAIChat(TimeStampedModel):
    # See https://platform.openai.com/docs/models#current-model-aliases
    MODELS = Choices("gpt-4o", "gpt-4o-mini", "chatgpt-4o-latest", "o1", "o1-mini")

    user = models.ForeignKey("users.User", related_name="chats", on_delete=models.CASCADE)
    model = models.CharField(
        null=False, blank=False, max_length=20, choices=MODELS, default=MODELS["gpt-4o-mini"]
    )
    tettra_page_category_filter = models.ForeignKey(
        "tettra.TettraPageCategory",
        related_name="openai_chats",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    tettra_page_subcategory_filter = models.ForeignKey(
        "tettra.TettraPageSubcategory",
        related_name="openai_chats",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    def save(self, *args, **kwargs):
        if self.tettra_page_category_filter is None:
            self.tettra_page_subcategory_filter = None
        elif (
            self.tettra_page_category_filter is not None
            and self.tettra_page_subcategory_filter is not None
        ):
            if not self.tettra_page_category_filter.tettra_pages.filter(
                subcategory=self.tettra_page_subcategory_filter
            ).exists():
                self.tettra_page_subcategory_filter = None
        return super(OpenAIChat, self).save(*args, **kwargs)


class OpenAIChatMessage(TimeStampedModel):
    ROLES = Choices(
        ("system", _("system")),
        ("user", _("user")),
        ("assistant", _("assistant")),
    )
    RATING = Choices(
        ("none", _("none")),
        ("thumbs_up", _("thumbs_up")),
        ("thumbs_down", _("thumbs_down")),
    )
    MAX_TETTRA_PAGE_CHUNKS = 9

    chat = models.ForeignKey(OpenAIChat, related_name="messages", on_delete=models.CASCADE)
    role = models.CharField(null=False, blank=False, max_length=9, choices=ROLES)
    content = models.TextField(null=False, blank=False)
    tettra_page_chunks = models.ManyToManyField(
        "tettra.TettraPageChunk",
        related_name="tettra_page_chunks",
        help_text=_("Similar tettra page chunks to the content of this message."),
        blank=True,
    )
    rating = models.CharField(
        null=False, blank=False, max_length=11, choices=RATING, default=RATING.none
    )

    @property
    def LangchainSchemaMessageClass(self) -> Type[BaseMessage]:
        if self.role == self.__class__.ROLES.system:
            return SystemMessage
        if self.role == self.__class__.ROLES.user:
            return HumanMessage
        if self.role == self.__class__.ROLES.assistant:
            return AIMessage

    def clean_fields(self, exclude=None):
        super().clean_fields(exclude=exclude)

        if self.role != OpenAIChatMessage.ROLES.assistant:
            valid_ratings = [OpenAIChatMessage.RATING.none]
            if self.rating not in valid_ratings:
                raise ValidationError(
                    dict(
                        rating=[
                            f"message with role {self.role} must have rating of {' or '.join(valid_ratings)} not {self.rating}"
                        ]
                    )
                )

    def save(self, *args, **kwargs):
        if self.id is not None:
            self.full_clean()
        return super(OpenAIChatMessage, self).save(*args, **kwargs)

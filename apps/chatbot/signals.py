from django.core.exceptions import ValidationError
from django.db.models.signals import m2m_changed

from .models import OpenAIChatMessage


def _validate_tettra_page_chunks(sender, instance: OpenAIChatMessage, **kwargs):
    count = instance.tettra_page_chunks.count()

    if instance.role == OpenAIChatMessage.ROLES.assistant:
        if count > OpenAIChatMessage.MAX_TETTRA_PAGE_CHUNKS:
            raise ValidationError(
                dict(
                    tettra_pages=[
                        f"max_count: {OpenAIChatMessage.MAX_TETTRA_PAGE_CHUNKS} tettra_page_chunks: {count}"
                    ]
                )
            )
    else:
        if count > 0:
            raise ValidationError(
                dict(
                    tettra_pages=[
                        f"Only messages with role {OpenAIChatMessage.ROLES.user} can have linked tettra page chunks"
                    ]
                )
            )


m2m_changed.connect(
    _validate_tettra_page_chunks,
    sender=OpenAIChatMessage.tettra_page_chunks.through,
    dispatch_uid="validate_tettra_page_chunks",
)

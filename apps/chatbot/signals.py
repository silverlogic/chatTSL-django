from django.core.exceptions import ValidationError
from django.db.models.signals import m2m_changed

from .models import OpenAIChatMessage


def _validate_tettra_pages(sender, instance: OpenAIChatMessage, **kwargs):
    tettra_pages_count = instance.tettra_pages.all().count()

    if instance.role == OpenAIChatMessage.ROLES.assistant:
        if tettra_pages_count > OpenAIChatMessage.MAX_TETTRA_PAGES:
            raise ValidationError(
                dict(
                    tettra_pages=[
                        f"max_count: {OpenAIChatMessage.MAX_TETTRA_PAGES} tettra_pages: {tettra_pages_count}"
                    ]
                )
            )
    else:
        if tettra_pages_count > 0:
            raise ValidationError(
                dict(
                    tettra_pages=[
                        f"Only messages with role {OpenAIChatMessage.ROLES.user} can have linked tettra pages"
                    ]
                )
            )


m2m_changed.connect(
    _validate_tettra_pages,
    sender=OpenAIChatMessage.tettra_pages.through,
    dispatch_uid="validate_tettra_pages",
)

from django.db import models

from .validators import validate_only_emojis


class EmojiField(models.CharField):
    default_validators = [validate_only_emojis]

    def __init__(self, *args, **kwargs):
        # 10 is the max length of an emoji
        kwargs["max_length"] = 10
        super().__init__(*args, **kwargs)

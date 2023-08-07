from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


def validate_OPEN_AI_CHAT_CONSUMER__LATEST_USER_MESSAGE_FOOTER(value: str):
    if value.count("{chat_message_content}") != 1:
        raise ValidationError(_("Must contain exactly one instance of {chat_message_content}"))

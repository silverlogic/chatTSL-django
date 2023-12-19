import re

from django.core.exceptions import ValidationError


def validate_only_emojis(value):
    # Regex pattern to match emojis
    emoji_pattern = re.compile(
        r"^("
        r"[\U0001F600-\U0001F64F]|"  # emoticons
        r"[\U0001F300-\U0001F5FF]|"  # symbols & pictographs
        r"[\U0001F680-\U0001F6FF]|"  # transport & map symbols
        r"[\U0001F700-\U0001F77F]|"  # alchemical symbols
        r"[\U0001F780-\U0001F7FF]|"  # Geometric Shapes Extended
        r"[\U0001F800-\U0001F8FF]|"  # Supplemental Arrows-C
        r"[\U0001F900-\U0001F9FF]|"  # Supplemental Symbols and Pictographs
        r"[\U0001FA00-\U0001FA6F]|"  # Chess Symbols
        r"[\U0001FA70-\U0001FAFF]|"  # Symbols and Pictographs Extended-A
        r"[\U00002702-\U000027B0]|"  # Dingbats
        r"[\U000024C2-\U0001F251]"  # Enclosed characters
        r")+$"  # Match one or more of the above
    )

    if not emoji_pattern.fullmatch(value):
        raise ValidationError("Only emojis are allowed.")

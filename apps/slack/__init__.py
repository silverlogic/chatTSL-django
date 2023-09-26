from django.conf import settings

from slack_sdk import WebClient

slack_bot_client = WebClient(token=settings.SLACK_BOT_OAUTH_TOKEN)

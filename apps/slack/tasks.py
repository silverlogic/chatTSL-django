from __future__ import annotations

import logging
from typing import Dict, Optional, Sequence, Union

from django.conf import settings

from celery import shared_task
from celery.result import AsyncResult
from constance import config
from langchain.schema import SystemMessage
from langchain_community.chat_models import ChatOpenAI
from slack_sdk.models import blocks

from apps.api.v1.chatbot.serializers import OpenAIChatMessageSerializer
from apps.chatbot.models import OpenAIChat, OpenAIChatMessage
from apps.slack import slack_bot_client

from .models import SlackEventCallbackData, SlackInstallation, SlackOpenAIChat
from .utils import get_or_create_user_for_slack_user

logger = logging.getLogger(__name__)


class _OpenAIChatController:
    """
    There might be a better way to do this, but this class is used to recreate the logic
    found in `OpenAIChatConsumer`. After done with any remaining slack integration stories,
    we should try to refactor this into a single class that can be used in the websocket consumer and here
    """

    chat: OpenAIChat

    def __init__(self, *args, chat: OpenAIChat, **kwargs):
        self.chat = chat

    def create_chat_message(self, data):
        from apps.api.v1.chatbot.serializers import OpenAIChatMessageSerializer

        data = dict(**data, chat=self.chat.id)
        serializer = OpenAIChatMessageSerializer(data=data, context=dict())
        serializer.is_valid(raise_exception=True)
        return serializer.save()

    def get_chat_messages(self):
        return list(self.chat.messages.all())

    def get_similar_tettra_page_chunks(self, text: str):
        from apps.chatbot.models import OpenAIChatMessage
        from apps.tettra.utils import find_similar

        self.chat.refresh_from_db()
        filter_value = getattr(config, "OPEN_AI_CHAT_CONSUMER__COSINE_DISTANCE_FILTER")
        filter_kwargs = dict(cosine_distance__lt=filter_value)
        if self.chat.tettra_page_category_filter is not None:
            filter_kwargs["tettra_page__category"] = self.chat.tettra_page_category_filter
        if self.chat.tettra_page_subcategory_filter is not None:
            filter_kwargs["tettra_page__subcategory"] = self.chat.tettra_page_subcategory_filter

        queryset = find_similar(text).filter(**filter_kwargs)
        return list(queryset[: OpenAIChatMessage.MAX_TETTRA_PAGE_CHUNKS])

    def get_constance_config_attr(self, attr: str):
        return getattr(config, attr)

    def handle_user_message(self, text) -> OpenAIChatMessage:
        user_chat_message: OpenAIChatMessage = self.create_chat_message(
            dict(role=OpenAIChatMessage.ROLES.user, **dict(content=text))
        )

        tettra_page_chunks = self.get_similar_tettra_page_chunks(user_chat_message.content)

        logger.info(
            f'Using similar tettra page chunks as context: {[f"{t.id} {t.cosine_distance}" for t in tettra_page_chunks]}',
        )

        chat_openai = ChatOpenAI(
            openai_api_key=settings.OPENAI_API_KEY, temperature=0, model=self.chat.model
        )
        chat_messages = self.get_chat_messages()
        messages = []
        for chat_message in chat_messages:
            _content = chat_message.content
            if chat_message.id == user_chat_message.id and len(tettra_page_chunks) > 0:
                header = self.get_constance_config_attr(
                    "OPEN_AI_CHAT_CONSUMER__LATEST_USER_MESSAGE_HEADER"
                )
                footer = self.get_constance_config_attr(
                    "OPEN_AI_CHAT_CONSUMER__LATEST_USER_MESSAGE_FOOTER"
                )
                footer = footer.format(chat_message_content=_content)
                _content = (
                    header
                    + "\n\n".join(
                        [tettra_page_chunk.content for tettra_page_chunk in tettra_page_chunks]
                    )
                    + "\n\n"
                    + footer
                )

            messages.append(chat_message.LangchainSchemaMessageClass(content=_content))
        system_message_text = self.get_constance_config_attr(
            "OPEN_AI_CHAT_CONSUMER__SYSTEM_MESSAGE"
        )
        messages.insert(
            0,
            SystemMessage(content=system_message_text),
        )
        for message in messages:
            logger.info(message.content)

        chat_response = chat_openai(messages)

        ai_chat_message = self.create_chat_message(
            dict(role=OpenAIChatMessage.ROLES.assistant, content=chat_response.content)
        )
        ai_chat_message.tettra_page_chunks.set(tettra_page_chunks)

        return ai_chat_message


@shared_task
def slack_handle_event_callback_message(slack_event_callback_data_id: int):
    slack_event_callback_data = SlackEventCallbackData.objects.get(id=slack_event_callback_data_id)
    data = slack_event_callback_data.data
    event: dict = data["event"]
    event_type = event["type"]
    if event_type == "tokens_revoked":
        # SEE https://api.slack.com/events/tokens_revoked
        # {
        #     'token': 'tJLDLso9TVHLCYsFYO7r6d9k',
        #     'team_id': 'T0280MA5P',
        #     'api_app_id': 'A05R643N400',
        #     'event': {
        #         'type': 'tokens_revoked',
        #         'tokens': {
        #             'oauth': [],
        #             'bot': ['U05QV7F97C1']
        #         },
        #         'event_ts': '1694035866.044349'},
        #         'type': 'event_callback',
        #         'event_id': 'Ev05RY1WJN1E',
        #         'event_time': 1694035866
        # }
        tokens = event.get("tokens", {})
        bot_user_ids = tokens.get("bot", [])
        SlackInstallation.objects.filter(
            slack_oauth_response__team__id=data["team_id"],
            slack_oauth_response__bot_user_id__in=bot_user_ids,
        ).delete()
    elif event_type == "app_uninstalled":
        # SEE https://api.slack.com/events/app_uninstalled
        # {
        #     'token': 'tJLDLso9TVHLCYsFYO7r6d9k',
        #     'team_id': 'T0280MA5P',
        #     'api_app_id': 'A05R643N400',
        #     'event': {
        #         'type': 'app_uninstalled',
        #         'event_ts': '1694035866.052202'
        #     },
        #     'type': 'event_callback',
        #     'event_id': 'Ev05QUFVQKHV',
        #     'event_time': 1694035866
        # }
        SlackInstallation.objects.filter(slack_oauth_response__team__id=data["team_id"]).delete()
    elif event_type == "message":
        is_bot = "bot_id" in event
        if is_bot:
            logger.info(f"Skipping event_type:{event_type}. Reason: is_bot:{is_bot}")
        else:
            # In the future if we have issues with duplicate messages from Slack
            # We can use this field to fix
            # client_msg_id = event["client_msg_id"]
            event_user: str = event["user"]
            is_in_thread = "thread_ts" in event

            user, _ = get_or_create_user_for_slack_user(slack_user_id=event_user)

            if not is_in_thread:
                logger.info(
                    f"Skipping event_type:{event_type}. Reason: is_in_thread:{is_in_thread}"
                )
            else:
                event_channel: str = event["channel"]
                event_thread_ts: str = event["thread_ts"]
                event_text: str = event["text"]
                slack_chat = (
                    SlackOpenAIChat.objects.filter(
                        slack_event_json__event__channel=event_channel,
                        slack_event_json__event__event_ts=event_thread_ts,
                    )
                    .order_by("-created")
                    .first()
                )

                if slack_chat:
                    if slack_chat.is_celery_task_processing:
                        slack_bot_client.chat_postMessage(
                            channel=event_channel,
                            text="Please wait, still processing the previous message",
                            thread_ts=event_thread_ts,
                        )
                    else:
                        result: AsyncResult = process_incoming_user_slack_message.apply_async(
                            kwargs=dict(slack_chat_id=slack_chat.id, slack_message_text=event_text)
                        )
                        slack_chat.celery_task_id = result.id
                        slack_chat.save()
    elif event_type == "app_mention":
        # In the future if we have issues with duplicate messages from Slack
        # We can use this field to fix
        # client_msg_id = event["client_msg_id"]
        event_user: str = event["user"]
        event_text: str = event["text"]
        is_in_thread = bool("thread_ts" in event)

        user, _ = get_or_create_user_for_slack_user(slack_user_id=event_user)

        if is_in_thread:
            logger.info(f"Skipping event_type:{event_type}. Reason: is_in_thread:{is_in_thread}")
        else:
            chat = OpenAIChat.objects.create(user=user)
            slack_chat = SlackOpenAIChat.objects.create(chat=chat, slack_event_json=data)

            result = process_incoming_user_slack_message.apply_async(
                kwargs=dict(slack_chat_id=slack_chat.id, slack_message_text=event_text)
            )
            slack_chat.celery_task_id = result.id
            slack_chat.save()

    slack_event_callback_data.delete()


@shared_task
def send_slack_message_to_slack_chat(
    slack_chat: Union[int, SlackOpenAIChat],
    text: Optional[str] = None,
    blocks: Optional[Union[str, Sequence[Union[Dict, blocks.Block]]]] = None,
):
    if not isinstance(slack_chat, SlackOpenAIChat):
        slack_chat = SlackOpenAIChat.objects.get(id=slack_chat)

    slack_event: dict = slack_chat.slack_event_json["event"]
    slack_channel: str = slack_event["channel"]
    slack_event_ts: str = slack_event.get("event_ts")

    slack_bot_client.chat_postMessage(
        channel=slack_channel, text=text, blocks=blocks, thread_ts=slack_event_ts
    )


@shared_task
def process_incoming_user_slack_message(slack_chat_id: int, slack_message_text: str):
    slack_chat = SlackOpenAIChat.objects.get(id=slack_chat_id)

    slack_event: dict = slack_chat.slack_event_json["event"]
    slack_channel: str = slack_event["channel"]
    slack_event_ts: str = slack_event.get("event_ts")

    chat_controller = _OpenAIChatController(chat=slack_chat.chat)
    ai_chat_message = chat_controller.handle_user_message(text=slack_message_text)
    ai_chat_message_serializer = OpenAIChatMessageSerializer(instance=ai_chat_message)

    slack_bot_client.chat_postMessage(
        channel=slack_channel,
        blocks=[
            dict(type="section", text=dict(type="mrkdwn", text=ai_chat_message.content)),
            *[
                dict(type="section", text=dict(type="mrkdwn", text=tettra_page_data["url"]))
                for tettra_page_data in ai_chat_message_serializer.data["tettra_pages"]
            ],
        ],
        text=ai_chat_message.content,
        thread_ts=slack_event_ts,
    )

import logging

from django.conf import settings

from celery import shared_task
from constance import config
from langchain.chat_models import ChatOpenAI
from langchain.schema import SystemMessage
from slack_sdk import WebClient

from apps.api.v1.chatbot.serializers import OpenAIChatMessageSerializer
from apps.chatbot.models import OpenAIChat, OpenAIChatMessage

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
def slack_handle_event_callback_message(request_data: dict):
    """
    Handle slack event_hook request data where
    type = 'event_callback'
    event_type = 'message'
    """

    type = request_data["type"]
    assert type == "event_callback"
    event = request_data["event"]
    event_type = event["type"]
    assert event_type == "message"
    event_user: str = event["user"]
    event_text: str = event["text"]

    slack_client = WebClient(token=settings.SLACK_BOT_OAUTH_TOKEN)

    user, _ = get_or_create_user_for_slack_user(slack_user_id=event_user)
    if user is None:
        return

    user_chats = user.chats.all().order_by("-created")
    chat: OpenAIChat
    if user_chats.exists():
        chat = user_chats.first()
    else:
        chat = OpenAIChat.objects.create(user=user)
    chat_controller = _OpenAIChatController(chat=chat)
    ai_chat_message = chat_controller.handle_user_message(text=event_text)
    ai_chat_message_serializer = OpenAIChatMessageSerializer(instance=ai_chat_message)

    slack_client.chat_postMessage(
        channel=event["channel"],
        blocks=[
            dict(type="section", text=dict(type="mrkdwn", text=ai_chat_message.content)),
            *[
                dict(type="section", text=dict(type="mrkdwn", text=tettra_page_data["url"]))
                for tettra_page_data in ai_chat_message_serializer.data["tettra_pages"]
            ],
        ],
        text=ai_chat_message.content,
    )

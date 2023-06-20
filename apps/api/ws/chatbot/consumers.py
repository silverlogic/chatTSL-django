import json
import logging

from django.conf import settings

from channels.db import database_sync_to_async
from channels.exceptions import StopConsumer
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from langchain.chat_models import ChatOpenAI
from langchain.schema import SystemMessage
from rest_framework import exceptions

logger = logging.getLogger(__name__)


class OpenAIChatConsumer(AsyncJsonWebsocketConsumer):
    from apps.chatbot.models import OpenAIChat

    chat_id: int
    chat: OpenAIChat
    group_name: str

    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)
        self.chat_id = None
        self.chat = None
        self.group_name = None

    async def connect(self):
        from apps.chatbot.models import OpenAIChat

        self.chat_id = self.scope["url_route"]["kwargs"]["chat_id"]
        try:
            self.chat = await database_sync_to_async(OpenAIChat.objects.get)(
                id=self.chat_id, user=self.scope["user"]
            )
            self.group_name = (
                f"{self.chat._meta.app_label}_{self.chat._meta.object_name}_{self.chat.id}"
            )
            await self.accept("Authorization")
            await self.channel_layer.group_add(self.group_name, self.channel_name)
        except BaseException as e:
            logger.error(f"{e}")
            await self.close()

    async def disconnect(self, close_code):
        if self.group_name:
            await self.channel_layer.group_discard(self.group_name, self.channel_name)
        raise StopConsumer()

    @database_sync_to_async
    def create_chat_message(self, data):
        from apps.api.v1.chatbot.serializers import OpenAIChatMessageSerializer

        serializer = OpenAIChatMessageSerializer(
            data=dict(**data, chat=self.chat_id), context=dict(scope=self.scope)
        )
        serializer.is_valid(raise_exception=True)
        return serializer.save()

    @database_sync_to_async
    def get_chat_messages(self):
        return list(self.chat.messages.all())

    @database_sync_to_async
    def get_similar_tettra_pages(self, text: str):
        from apps.tettra.utils import find_similar

        queryset = find_similar(text).filter(cosine_distance__lt=0.6)
        return list(queryset[:3])

    async def receive(self, text_data=None, bytes_data=None, **kwargs):
        from apps.api.v1.chatbot.serializers import OpenAIChatMessageSerializer
        from apps.chatbot.models import OpenAIChatMessage
        from apps.tettra.utils import get_text_to_embed

        from .serializers import InputEventSerializer, OutputEventSerializer
        from .types import INPUT_EVENT_TYPE, OUTPUT_EVENT_TYPE

        input_event_serializer: InputEventSerializer
        try:
            data = json.loads(text_data)
            input_event_serializer = InputEventSerializer(data=data, context=dict(scope=self.scope))
        except Exception:
            logger.error(f"Failed to convert text to json {text_data}")
            return

        try:
            input_event_serializer.is_valid(raise_exception=True)

            if input_event_serializer.validated_data["event_type"] == INPUT_EVENT_TYPE.ping:
                output_event_serializer = OutputEventSerializer(
                    data=dict(event_type=OUTPUT_EVENT_TYPE.pong, event_data={})
                )
                output_event_serializer.is_valid(raise_exception=True)
                await self.send_json(output_event_serializer.validated_data)

            if (
                input_event_serializer.validated_data["event_type"]
                == INPUT_EVENT_TYPE.create_message
            ):
                user_chat_message: OpenAIChatMessage = await self.create_chat_message(
                    dict(
                        role=OpenAIChatMessage.ROLES.user,
                        **input_event_serializer.validated_data["event_data"],
                    )
                )
                user_chat_message_serializer = OpenAIChatMessageSerializer(
                    instance=user_chat_message
                )

                output_event_serializer = OutputEventSerializer(
                    data=dict(
                        event_type=OUTPUT_EVENT_TYPE.on_message_created,
                        event_data=user_chat_message_serializer.data,
                    )
                )
                output_event_serializer.is_valid(raise_exception=True)
                await self.send_json(output_event_serializer.validated_data)

                tettra_pages = await self.get_similar_tettra_pages(user_chat_message.content)
                logger.info(
                    f'Using similar tettra pages as context: {[f"{t.id} {t.cosine_distance}" for t in tettra_pages]}',
                )

                chat = ChatOpenAI(
                    openai_api_key=settings.OPENAI_API_KEY, temperature=0, model=self.chat.model
                )
                chat_messages = await self.get_chat_messages()
                messages = []
                for chat_message in chat_messages:
                    _content = chat_message.content
                    if chat_message.id == user_chat_message.id and len(tettra_pages) > 0:
                        header = "Answer the question using the provided context.\n\nContext:\n"
                        footer = (
                            "\n\nQuestion: "
                            + _content
                            + "\n\nReturn detailed answers that explain a process in multiple steps in html format."
                        )
                        _content = (
                            header
                            + " ".join(
                                [get_text_to_embed(tettra_page) for tettra_page in tettra_pages]
                            )
                            + footer
                        )

                    messages.append(chat_message.LangchainSchemaMessageClass(content=_content))
                messages.insert(
                    0,
                    SystemMessage(
                        content="You are a helpful assistant. Return detailed answers that explain a process in multiple steps."
                    ),
                )
                logger.error(f"----------{self.chat_id}----------")
                for message in messages:
                    logger.error(message.content)
                logger.error(f"----------{self.chat_id}----------")

                chat_response = chat(messages)
                ai_chat_message = await self.create_chat_message(
                    dict(role=OpenAIChatMessage.ROLES.assistant, content=chat_response.content)
                )
                ai_chat_message_serializer = OpenAIChatMessageSerializer(instance=ai_chat_message)

                output_event_serializer = OutputEventSerializer(
                    data=dict(
                        event_type=OUTPUT_EVENT_TYPE.on_message_created,
                        event_data=ai_chat_message_serializer.data,
                    )
                )
                output_event_serializer.is_valid(raise_exception=True)
                await self.send_json(output_event_serializer.validated_data)
        except exceptions.ValidationError as e:
            logger.error(json.dumps(e.get_full_details(), indent=4))

            output_event_serializer = OutputEventSerializer(
                data=dict(event_type=OUTPUT_EVENT_TYPE.event_data, event_data=e.get_full_details())
            )
            output_event_serializer.is_valid(raise_exception=True)
            await self.send_json(output_event_serializer.validated_data)

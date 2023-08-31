import json
import logging
from typing import Any

from django.conf import settings

from asgiref.sync import sync_to_async
from channels.db import database_sync_to_async
from channels.exceptions import StopConsumer
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from constance import config
from langchain.chat_models import ChatOpenAI
from langchain.schema import SystemMessage
from rest_framework import exceptions, serializers

logger = logging.getLogger(__name__)


class OpenAIChatConsumer(AsyncJsonWebsocketConsumer):
    chat_id: int
    chat: Any
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

        data = dict(**data, chat=self.chat_id)
        serializer = OpenAIChatMessageSerializer(data=data, context=dict(scope=self.scope))
        serializer.is_valid(raise_exception=True)
        return serializer.save()

    @database_sync_to_async
    def get_chat_messages(self):
        return list(self.chat.messages.all())

    @database_sync_to_async
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

    @database_sync_to_async
    def get_serializer_data(self, serializer: serializers.ModelSerializer):
        return serializer.data

    @sync_to_async
    def get_constance_config_attr(self, attr: str):
        return getattr(config, attr)

    async def receive(self, text_data=None, bytes_data=None, **kwargs):
        from apps.api.v1.chatbot.serializers import OpenAIChatMessageSerializer
        from apps.chatbot.models import OpenAIChatMessage

        from .serializers import InputEventSerializer, OutputEventSerializer
        from .types import INPUT_EVENT_TYPE, OUTPUT_EVENT_TYPE

        input_event_serializer: InputEventSerializer
        try:
            data = json.loads(text_data)
            input_event_serializer = InputEventSerializer(data=data, context=dict(scope=self.scope))
        except Exception:
            logger.error(f"Failed to convert text to json {text_data}")
            return

        logger.info("{:-^100s}".format(f"BEGIN {self.receive.__name__}(chat_id:{self.chat_id})"))

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
                        event_data=await self.get_serializer_data(user_chat_message_serializer),
                    )
                )
                output_event_serializer.is_valid(raise_exception=True)
                await self.send_json(output_event_serializer.validated_data)

                tettra_page_chunks = await self.get_similar_tettra_page_chunks(
                    user_chat_message.content
                )
                logger.info(
                    f'Using similar tettra page chunks as context: {[f"{t.id} {t.cosine_distance}" for t in tettra_page_chunks]}',
                )

                chat_openai = ChatOpenAI(
                    openai_api_key=settings.OPENAI_API_KEY, temperature=0, model=self.chat.model
                )
                chat_messages = await self.get_chat_messages()
                messages = []
                for chat_message in chat_messages:
                    _content = chat_message.content
                    if chat_message.id == user_chat_message.id and len(tettra_page_chunks) > 0:
                        header = await self.get_constance_config_attr(
                            "OPEN_AI_CHAT_CONSUMER__LATEST_USER_MESSAGE_HEADER"
                        )
                        footer = await self.get_constance_config_attr(
                            "OPEN_AI_CHAT_CONSUMER__LATEST_USER_MESSAGE_FOOTER"
                        )
                        footer = footer.format(chat_message_content=_content)
                        _content = (
                            header
                            + "\n\n".join(
                                [
                                    tettra_page_chunk.content
                                    for tettra_page_chunk in tettra_page_chunks
                                ]
                            )
                            + "\n\n"
                            + footer
                        )

                    messages.append(chat_message.LangchainSchemaMessageClass(content=_content))
                system_message_text = await self.get_constance_config_attr(
                    "OPEN_AI_CHAT_CONSUMER__SYSTEM_MESSAGE"
                )
                messages.insert(
                    0,
                    SystemMessage(content=system_message_text),
                )
                for message in messages:
                    logger.info(message.content)

                chat_response = chat_openai(messages)

                ai_chat_message = await self.create_chat_message(
                    dict(role=OpenAIChatMessage.ROLES.assistant, content=chat_response.content)
                )
                await database_sync_to_async(ai_chat_message.tettra_page_chunks.set)(
                    tettra_page_chunks
                )
                ai_chat_message_serializer = OpenAIChatMessageSerializer(instance=ai_chat_message)

                output_event_serializer = OutputEventSerializer(
                    data=dict(
                        event_type=OUTPUT_EVENT_TYPE.on_message_created,
                        event_data=await self.get_serializer_data(ai_chat_message_serializer),
                    )
                )
                output_event_serializer.is_valid(raise_exception=True)
                await self.send_json(output_event_serializer.validated_data)
        except exceptions.ValidationError as e:
            logger.error(json.dumps(e.get_full_details(), indent=4))

            output_event_serializer = OutputEventSerializer(
                data=dict(event_type=OUTPUT_EVENT_TYPE.on_error, event_data=e.get_full_details())
            )
            output_event_serializer.is_valid(raise_exception=True)
            await self.send_json(output_event_serializer.validated_data)
        except BaseException as e:
            logging.critical(e, exc_info=True)

            output_event_serializer = OutputEventSerializer(
                data=dict(
                    event_type=OUTPUT_EVENT_TYPE.on_error,
                    event_data={"error": ["An unknown error has occured. See logs for details."]},
                )
            )
            output_event_serializer.is_valid(raise_exception=True)
            await self.send_json(output_event_serializer.validated_data)

        logger.info("{:-^100s}".format(f"END {self.receive.__name__}(chat_id:{self.chat_id})"))

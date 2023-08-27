import pytest
from asgiref.sync import sync_to_async
from channels.testing import WebsocketCommunicator

from apps.asgi import application

import tests.factories as f
from tests.mixins import ApiMixin

pytestmark = pytest.mark.django_db


class TestOpenAIChatConsumerConsumer(ApiMixin):
    async def use_factory(self, factory_cls, *args, **kwargs):
        instance = await sync_to_async(factory_cls)(*args, **kwargs)
        return instance

    @pytest.fixture
    def communicator(self, async_user_client):
        self.client = async_user_client
        async_user_client.user.save()
        self.chat = f.OpenAIChat(user=async_user_client.user)
        self.chat.save()
        return WebsocketCommunicator(
            application,
            self.channels_reverse("ws-chat", kwargs=dict(chat_id=self.chat.id)),
            subprotocols=["Authorization", async_user_client.token.key],
        )

    @pytest.mark.asyncio
    async def test_anon_user_cant_connect(self):
        user = await self.use_factory(f.UserFactory)
        chat = await self.use_factory(f.OpenAIChat, user=user)
        await sync_to_async(chat.save)()
        communicator = WebsocketCommunicator(
            application, f"/ws/chat/{chat.id}/", subprotocols=["Authorization", ""]
        )
        connected, _ = await communicator.connect()
        assert not connected
        await communicator.disconnect()

    async def connect_and_assert_connection(self, communicator):
        connected, _ = await communicator.connect()
        assert connected

    @pytest.mark.asyncio
    @pytest.mark.skip("Finish implementing PS")
    async def test_ping(self, communicator, async_user_client):
        await self.connect_and_assert_connection(communicator)
        await communicator.send_json_to(dict(event_type="PING", event_data={}))
        response = await communicator.receive_json_from()
        print(response)

    @pytest.mark.asyncio
    @pytest.mark.skip("Finish implementing PS")
    async def test_create_message(self, communicator, async_user_client):
        pass

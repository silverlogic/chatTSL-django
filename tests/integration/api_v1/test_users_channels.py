import pytest
from channels.testing import WebsocketCommunicator

from apps.asgi import application

pytestmark = pytest.mark.django_db
from rest_framework import RemovedInDRF315Warning


class TestUsersChannels:
    @pytest.mark.asyncio
    async def test_user_can_connect(self, async_user_client):
        communicator = WebsocketCommunicator(
            application, "/ws/users/", subprotocols=["Authorization", async_user_client.token.key]
        )
        connected, subprotocol = await communicator.connect(timeout=10)
        assert connected
        message = await communicator.receive_json_from()
        assert message["type"] == "websocket_accept"
        await communicator.disconnect(timeout=10)

    @pytest.mark.asyncio
    async def test_anon_cant_connect(self):
        communicator = WebsocketCommunicator(
            application, "/ws/users/", subprotocols=["Authorization", ""]
        )
        connected, subprotocol = await communicator.connect(timeout=10)
        assert not connected
        await communicator.disconnect(timeout=10)

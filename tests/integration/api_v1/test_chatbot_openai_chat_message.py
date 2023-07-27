import pytest

from apps.chatbot.models import OpenAIChatMessage

import tests.factories as f
import tests.helpers as h
from tests.mixins import ApiMixin

pytestmark = pytest.mark.django_db


class TestOpenAIChatMessagesMixin(ApiMixin):
    def check_data_keys(self, data):
        if isinstance(data, dict):
            if set(data.keys()) == {"count", "next", "previous", "results"}:
                self.check_data_keys(data["results"])
            else:
                assert set(data.keys()) == {
                    "id",
                    "chat",
                    "role",
                    "content",
                    "tettra_pages",
                    "rating",
                }
        elif isinstance(data, list):
            for element in data:
                self.check_data_keys(element)
        else:
            assert False


class TestOpenAIChatMessagesDetailMixin(TestOpenAIChatMessagesMixin):
    view_name = "chatbot-open-ai-messages-detail"


class TestOpenAIChatMessagesListMixin(TestOpenAIChatMessagesMixin):
    view_name = "chatbot-open-ai-messages-list"


class TestOpenAIChatMessagesCreate(TestOpenAIChatMessagesListMixin):
    def test_anon_cant_create(self, client):
        chat = f.OpenAIChatFactory(user=f.UserFactory())
        r = client.post(
            self.reverse(), dict(chat=chat.id, role=OpenAIChatMessage.ROLES.user, content="Test")
        )
        h.responseUnauthorized(r)

    def test_user_can_create_with_owned_chat(self, user_client):
        chat = f.OpenAIChatFactory(user=user_client.user)
        r = user_client.post(
            self.reverse(), dict(chat=chat.id, role=OpenAIChatMessage.ROLES.user, content="Test")
        )
        h.responseCreated(r)
        self.check_data_keys(r.data)

    def test_user_cant_create_with_unowned_chat(self, user_client):
        chat = f.OpenAIChatFactory(user=f.UserFactory())
        r = user_client.post(
            self.reverse(), dict(chat=chat.id, role=OpenAIChatMessage.ROLES.user, content="Test")
        )
        h.responseNotFound(r)


class TestOpenAIChatMessagesRetrieve(TestOpenAIChatMessagesDetailMixin):
    def test_anon_cant_retrieve(self, client):
        instance = f.OpenAIChatFactory(user=f.UserFactory())
        r = client.get(self.reverse(kwargs={"pk": instance.id}))
        h.responseUnauthorized(r)

    def test_user_can_retrieve_owned(self, user_client):
        instance = f.OpenAIChatMessageFactory(chat=f.OpenAIChatFactory(user=user_client.user))
        r = user_client.get(self.reverse(kwargs={"pk": instance.id}))
        h.responseOk(r)
        self.check_data_keys(r.data)

    def test_user_cant_retrieve_unowned(self, user_client):
        instance = f.OpenAIChatMessageFactory(chat=f.OpenAIChatFactory(user=f.UserFactory()))
        r = user_client.get(self.reverse(kwargs={"pk": instance.id}))
        h.responseNotFound(r)


class TestOpenAIChatMessagesList(TestOpenAIChatMessagesListMixin):
    def test_anon_cant_list(self, client):
        r = client.get(self.reverse())
        h.responseUnauthorized(r)

    def test_user_can_list(self, user_client):
        f.OpenAIChatMessageFactory.create_batch(
            size=7, chat=f.OpenAIChatFactory(user=f.UserFactory())
        )
        f.OpenAIChatMessageFactory.create_batch(
            size=7, chat=f.OpenAIChatFactory(user=user_client.user)
        )
        r = user_client.get(self.reverse())
        h.responseOk(r)
        assert len(r.data["results"]) == 7
        self.check_data_keys(r.data)


class TestOpenAIChatMessagesDestroy(TestOpenAIChatMessagesDetailMixin):
    def test_anon_cant_destroy(self, client):
        instance = f.OpenAIChatMessageFactory(chat=f.OpenAIChatFactory(user=f.UserFactory()))
        r = client.delete(self.reverse(kwargs={"pk": instance.id}))
        h.responseUnauthorized(r)

    def test_user_can_destroy_owned(self, user_client):
        instance = f.OpenAIChatMessageFactory(chat=f.OpenAIChatFactory(user=user_client.user))
        r = user_client.delete(self.reverse(kwargs={"pk": instance.id}))
        h.responseOk(r)
        self.check_data_keys(r.data)

    def test_user_cant_destroy_unowned(self, user_client):
        instance = f.OpenAIChatMessageFactory(chat=f.OpenAIChatFactory(user=f.UserFactory()))
        r = user_client.delete(self.reverse(kwargs={"pk": instance.id}))
        h.responseNotFound(r)


class TestOpenAIChatMessagesUpdate(TestOpenAIChatMessagesDetailMixin):
    def test_anon_cant_update(self, client):
        instance = f.OpenAIChatMessageFactory(
            chat=f.OpenAIChatFactory(user=f.UserFactory()), role=OpenAIChatMessage.ROLES.assistant
        )
        r = client.patch(
            self.reverse(kwargs={"pk": instance.id}),
            dict(rating=OpenAIChatMessage.RATING.thumbs_up),
        )
        h.responseUnauthorized(r)

    def test_user_can_update_owned(self, user_client):
        instance = f.OpenAIChatMessageFactory(
            chat=f.OpenAIChatFactory(user=user_client.user), role=OpenAIChatMessage.ROLES.assistant
        )
        r = user_client.patch(
            self.reverse(kwargs={"pk": instance.id}),
            dict(rating=OpenAIChatMessage.RATING.thumbs_up),
        )
        h.responseOk(r)
        self.check_data_keys(r.data)
        assert r.data["rating"] == OpenAIChatMessage.RATING.thumbs_up

    def test_user_cant_update_unowned(self, user_client):
        instance = f.OpenAIChatMessageFactory(
            chat=f.OpenAIChatFactory(user=f.UserFactory()), role=OpenAIChatMessage.ROLES.assistant
        )
        r = user_client.patch(
            self.reverse(kwargs={"pk": instance.id}),
            dict(rating=OpenAIChatMessage.RATING.thumbs_up),
        )
        h.responseNotFound(r)

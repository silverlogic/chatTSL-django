import pytest

import tests.factories as f
import tests.helpers as h
from tests.mixins import ApiMixin

pytestmark = pytest.mark.django_db


class TestOpenAIChatsMixin(ApiMixin):
    def check_data_keys(self, data):
        if isinstance(data, dict):
            if set(data.keys()) == {"count", "next", "previous", "results"}:
                self.check_data_keys(data["results"])
            else:
                assert set(data.keys()) == {
                    "id",
                    "user",
                    "model",
                    "messages",
                    "tettra_page_category_filter",
                    "tettra_page_subcategory_filter",
                }
        elif isinstance(data, list):
            for element in data:
                self.check_data_keys(element)
        else:
            assert False


class TestOpenAIChatsDetailMixin(TestOpenAIChatsMixin):
    view_name = "chatbot-open-ai-detail"


class TestOpenAIChatsListMixin(TestOpenAIChatsMixin):
    view_name = "chatbot-open-ai-list"


class TestOpenAIChatsCreate(TestOpenAIChatsListMixin):
    def test_anon_cant_create(self, client):
        r = client.post(self.reverse(), dict(model="gpt-4o"))
        h.responseUnauthorized(r)

    def test_user_can_create(self, user_client):
        r = user_client.post(self.reverse(), dict(model="gpt-4o"))
        h.responseCreated(r)
        self.check_data_keys(r.data)


class TestOpenAIChatsRetrieve(TestOpenAIChatsDetailMixin):
    def test_anon_cant_retrieve(self, client):
        instance = f.OpenAIChatFactory(user=f.UserFactory())
        r = client.get(self.reverse(kwargs={"pk": instance.id}))
        h.responseUnauthorized(r)

    def test_user_can_retrieve_owned(self, user_client):
        instance = f.OpenAIChatFactory(user=user_client.user)
        r = user_client.get(self.reverse(kwargs={"pk": instance.id}))
        h.responseOk(r)
        self.check_data_keys(r.data)

    def test_user_cant_retrieve_unowned(self, user_client):
        instance = f.OpenAIChatFactory(user=f.UserFactory())
        r = user_client.get(self.reverse(kwargs={"pk": instance.id}))
        h.responseNotFound(r)


class TestOpenAIChatsList(TestOpenAIChatsListMixin):
    def test_anon_cant_list(self, client):
        r = client.get(self.reverse())
        h.responseUnauthorized(r)

    def test_user_can_list(self, user_client):
        f.OpenAIChatFactory.create_batch(size=7, user=f.UserFactory())
        f.OpenAIChatFactory.create_batch(size=7, user=user_client.user)
        r = user_client.get(self.reverse())
        h.responseOk(r)
        assert len(r.data["results"]) == 7
        self.check_data_keys(r.data)


class TestOpenAIChatsUpdate(TestOpenAIChatsDetailMixin):
    def test_anon_cant_update(self, client):
        instance = f.OpenAIChatFactory(user=f.UserFactory())
        r = client.patch(self.reverse(kwargs={"pk": instance.id}), dict())
        h.responseUnauthorized(r)

    def test_user_cant_update_unowned_chat(self, user_client):
        instance = f.OpenAIChatFactory(user=f.UserFactory(), model="gpt-4o")
        r = user_client.patch(self.reverse(kwargs={"pk": instance.id}), dict(model="o1-mini"))
        h.responseNotFound(r)

    def test_user_can_update_owned_chat(self, user_client):
        instance = f.OpenAIChatFactory(user=user_client.user, model="gpt-4o")
        r = user_client.patch(self.reverse(kwargs={"pk": instance.id}), dict(model="o1-mini"))
        h.responseOk(r)
        self.check_data_keys(r.data)
        instance.refresh_from_db()
        assert instance.model == "o1-mini"

    def test_updating_category_updates_subcategory(self, user_client):
        tettra_page_1 = f.TettraPageFactory()
        tettra_page_2 = f.TettraPageFactory()
        instance = f.OpenAIChatFactory(
            user=user_client.user,
            tettra_page_category_filter=tettra_page_1.category,
            tettra_page_subcategory_filter=tettra_page_1.subcategory,
        )
        r = user_client.patch(
            self.reverse(kwargs={"pk": instance.id}),
            dict(tettra_page_category_filter=tettra_page_2.category.id),
        )
        h.responseOk(r)
        self.check_data_keys(r.data)
        instance.refresh_from_db()
        assert instance.tettra_page_subcategory_filter is None


class TestOpenAIChatsDestroy(TestOpenAIChatsDetailMixin):
    def test_anon_cant_destroy(self, client):
        instance = f.OpenAIChatFactory(user=f.UserFactory())
        r = client.delete(self.reverse(kwargs={"pk": instance.id}))
        h.responseUnauthorized(r)

    def test_user_can_destroy_owned(self, user_client):
        instance = f.OpenAIChatFactory(user=user_client.user)
        r = user_client.delete(self.reverse(kwargs={"pk": instance.id}))
        h.responseOk(r)
        self.check_data_keys(r.data)

    def test_user_cant_destroy_unowned(self, user_client):
        instance = f.OpenAIChatFactory(user=f.UserFactory())
        r = user_client.delete(self.reverse(kwargs={"pk": instance.id}))
        h.responseNotFound(r)

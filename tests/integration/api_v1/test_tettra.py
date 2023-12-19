from unittest.mock import patch

import pytest

import tests.factories as f
import tests.helpers as h
from tests.mixins import ApiMixin

pytestmark = pytest.mark.django_db


class TestTettraPageCategoriesMixin(ApiMixin):
    def check_data_keys(self, data):
        if isinstance(data, dict):
            if set(data.keys()) == {"count", "next", "previous", "results"}:
                self.check_data_keys(data["results"])
            else:
                assert set(data.keys()) == {"id", "category_id", "category_name"}
        elif isinstance(data, list):
            for element in data:
                self.check_data_keys(element)
        else:
            assert False


class TestTettraPageCategoriesDetailMixin(TestTettraPageCategoriesMixin):
    view_name = "tettra-categories-detail"


class TestTettraPageCategoriesListMixin(TestTettraPageCategoriesMixin):
    view_name = "tettra-categories-list"


class TestTettraPageCategoriesList(TestTettraPageCategoriesListMixin):
    def test_anon_cant_list(self, client):
        r = client.get(self.reverse())
        h.responseUnauthorized(r)

    def test_user_can_list(self, user_client):
        f.TettraPageCategoryFactory.create_batch(size=7)
        r = user_client.get(self.reverse())
        h.responseOk(r)
        assert len(r.data) == 7
        self.check_data_keys(r.data)


class TestTettraPageSubcategoriesMixin(ApiMixin):
    def check_data_keys(self, data):
        if isinstance(data, dict):
            if set(data.keys()) == {"count", "next", "previous", "results"}:
                self.check_data_keys(data["results"])
            else:
                assert set(data.keys()) == {
                    "id",
                    "subcategory_id",
                    "subcategory_name",
                    "subcategory_icon",
                }
        elif isinstance(data, list):
            for element in data:
                self.check_data_keys(element)
        else:
            assert False


class TestTettraPageSubcategoriesDetailMixin(TestTettraPageSubcategoriesMixin):
    view_name = "tettra-subcategories-detail"


class TestTettraPageSubcategoriesListMixin(TestTettraPageSubcategoriesMixin):
    view_name = "tettra-subcategories-list"


class TestTettraPageSubcategoriesList(TestTettraPageSubcategoriesListMixin):
    def test_anon_cant_list(self, client):
        r = client.get(self.reverse())
        h.responseUnauthorized(r)

    def test_user_can_list(self, user_client):
        f.TettraPageSubcategoryFactory.create_batch(size=7)
        r = user_client.get(self.reverse())
        h.responseOk(r)
        assert len(r.data) == 7
        self.check_data_keys(r.data)

    @patch("apps.tettra.tasks.generate_vector_embeddings")
    def test_user_can_list_filter(self, mock_generate_vector_embeddings, user_client):
        mock_generate_vector_embeddings.return_value = None
        category = f.TettraPageCategoryFactory()
        f.TettraPageFactory.create_batch(size=7)
        f.TettraPageFactory.create_batch(size=7, category=category)
        r = user_client.get(self.reverse(query_params=dict(category_id=category.category_id)))
        h.responseOk(r)
        assert len(r.data) == 7
        self.check_data_keys(r.data)

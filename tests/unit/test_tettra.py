import operator

import pytest
from numpy.testing import assert_array_compare

import tests.factories as f

pytestmark = pytest.mark.django_db
VECTOR_DIM = 384


def test_can_save_embedding():
    tettra_page = f.TettraPageFactory()
    tettra_page.refresh_from_db()
    prev_embedding = tettra_page.embedding

    tettra_page.page_title += " extra"
    tettra_page.save()
    tettra_page.refresh_from_db()

    assert (
        len(prev_embedding) == VECTOR_DIM and len(tettra_page.embedding) == VECTOR_DIM
    )  # this is the vector dimension that should be the same as the model embedding field
    assert_array_compare(operator.__ne__, prev_embedding, tettra_page.embedding)

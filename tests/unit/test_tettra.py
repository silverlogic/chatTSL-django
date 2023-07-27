import operator

import pytest
from numpy.testing import assert_array_compare

import tests.factories as f

pytestmark = pytest.mark.django_db
VECTOR_DIM = 384


def test_can_save_embedding():
    tettra_page = f.TettraPageFactory()
    tettra_page.refresh_from_db()
    # The factory for this model is small enough to ensure there is only a single chunk
    assert tettra_page.chunks.count() == 1
    prev_embedding = tettra_page.chunks.first().embedding

    tettra_page.page_title += " extra"
    tettra_page.save()
    tettra_page.refresh_from_db()
    assert tettra_page.chunks.count() == 1
    embedding = tettra_page.chunks.first().embedding

    assert (
        len(prev_embedding) == VECTOR_DIM and len(embedding) == VECTOR_DIM
    )  # this is the vector dimension that should be the same as the model embedding field
    assert_array_compare(operator.__ne__, prev_embedding, embedding)

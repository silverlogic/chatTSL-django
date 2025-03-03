from __future__ import annotations

import itertools
import logging
from collections.abc import Generator
from contextlib import contextmanager
from typing import List, Tuple

from django.db.models.manager import BaseManager

from bs4 import BeautifulSoup
from langchain.text_splitter import Language, RecursiveCharacterTextSplitter
from langchain_huggingface.embeddings import HuggingFaceEmbeddings
from pgvector.django import CosineDistance

from .models import TettraPage, TettraPageChunk

logger = logging.getLogger(__name__)

TEXT_EMBEDDING_CHUNK_SIZE = 256
TEXT_EMBEDDING_CHUNK_OVERLAP = 30


def generate_vector_embeddings(tettra_page: TettraPage):
    tettra_page.chunks.all().delete()
    chunk_header = "FROM: {content}".format(
        content=" / ".join(
            list(
                itertools.filterfalse(
                    lambda item: not item,
                    [
                        tettra_page.category.category_name,
                        getattr(tettra_page.subcategory, "subcategory_name", None),
                        tettra_page.page_title,
                    ],
                )
            )
        )
    )
    text_splitter = RecursiveCharacterTextSplitter.from_language(
        Language.HTML,
        chunk_size=TEXT_EMBEDDING_CHUNK_SIZE,
        chunk_overlap=TEXT_EMBEDDING_CHUNK_OVERLAP,
    )
    html_chunks = text_splitter.split_text(tettra_page.html)
    html_text_chunks = [
        BeautifulSoup(html_chunk, features="html.parser").get_text().strip()
        for html_chunk in html_chunks
    ]
    html_text_chunks = list(
        itertools.filterfalse(lambda html_text_chunk: len(html_text_chunk) == 0, html_text_chunks)
    )
    text_chunks = [
        "\n".join([chunk_header, html_text_chunk]) for html_text_chunk in html_text_chunks
    ]
    text_chunk_embedding_pairs = embed(text_chunks)
    TettraPageChunk.objects.bulk_create(
        [
            TettraPageChunk(
                tettra_page=tettra_page,
                content=text_chunk_embedding_pair[0],
                embedding=text_chunk_embedding_pair[1],
            )
            for text_chunk_embedding_pair in text_chunk_embedding_pairs
        ]
    )


@contextmanager
def hugging_face_embeddings(*args, **kwds) -> Generator[HuggingFaceEmbeddings, None, None]:
    model_name = "sentence-transformers/all-MiniLM-L6-v2"
    model_kwargs = {"device": "cpu"}
    encode_kwargs = {"normalize_embeddings": False}
    embeddings = HuggingFaceEmbeddings(
        model_name=model_name, model_kwargs=model_kwargs, encode_kwargs=encode_kwargs
    )
    yield embeddings


def embed(text_array: List[str]) -> List[Tuple[str, List[float]]]:
    """
    Accepts string or list of strings and returns the string/embedding pair
    """
    with hugging_face_embeddings() as embeddings:
        return zip(text_array, embeddings._client.encode(text_array, show_progress_bar=False))


def find_similar(query: str) -> BaseManager[TettraPageChunk]:
    with hugging_face_embeddings() as embeddings:
        query_vector = embeddings.embed_query(query)
        queryset = (
            TettraPageChunk.objects.annotate(
                cosine_distance=CosineDistance("embedding", query_vector)
            )
            .order_by("cosine_distance")
            .filter(
                cosine_distance__isnull=False,
            )
        )

        return queryset

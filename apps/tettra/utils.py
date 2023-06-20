from __future__ import annotations

import logging
from typing import Any, Iterable, List, Optional, Type

from django.db.models.manager import BaseManager

from bs4 import BeautifulSoup
from langchain.docstore.document import Document
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.text_splitter import TokenTextSplitter
from langchain.vectorstores.base import VectorStore
from numpy import array, average
from pgvector.django import CosineDistance

from .models import TettraPage

TEXT_EMBEDDING_CHUNK_SIZE = 256

logger = logging.getLogger(__name__)


def generate_vector_embeddings(tettra_page: TettraPage):
    text = get_text_to_embed(tettra_page=tettra_page)
    tettra_page.embedding = get_embedding(text)
    tettra_page.save()


def get_embedding(text):
    """Return a list of tuples (text_chunk, embedding) and an average embedding for a text."""
    text_splitter = TokenTextSplitter(
        encoding_name="cl100k_base",
        chunk_size=TEXT_EMBEDDING_CHUNK_SIZE,
        chunk_overlap=int(TEXT_EMBEDDING_CHUNK_SIZE / 4),
    )
    text_chunks = text_splitter.split_text(text)

    try:
        embeddings = embed(text_chunks)
    except BaseException as e:
        logger.error(f"{e}")

    embedding = get_col_average_from_list_of_lists(embeddings)

    return embedding


def embed(text_array):
    """
    Accepts string or list of strings
    """
    model_name = "sentence-transformers/all-MiniLM-L6-v2"
    model_kwargs = {"device": "cpu"}
    encode_kwargs = {"normalize_embeddings": False}
    embeddings = HuggingFaceEmbeddings(
        model_name=model_name, model_kwargs=model_kwargs, encode_kwargs=encode_kwargs
    )
    return embeddings.client.encode(text_array, show_progress_bar=False)


def get_col_average_from_list_of_lists(list_of_lists):
    """Return the average of each column in a list of lists."""
    if len(list_of_lists) == 1:
        return list_of_lists[0]
    else:
        list_of_lists_array = array(list_of_lists)
        average_embedding = average(list_of_lists_array, axis=0)
        return average_embedding.tolist()


def get_text_to_embed(tettra_page: TettraPage):
    soup = BeautifulSoup(tettra_page.html, features="html.parser")
    return f"Title: {tettra_page.page_title} \n\n {soup.get_text()}"


def find_similar(query: str) -> BaseManager[TettraPage]:
    query_vector = get_embedding(query)
    queryset = (
        TettraPage.objects.annotate(cosine_distance=CosineDistance("embedding", query_vector))
        .order_by("cosine_distance")
        .filter(
            cosine_distance__isnull=False,
        )
    )

    return queryset


class PreComputedEmbeddingVectorStore(VectorStore):
    """
    A custom vector store where the raw embeddings are passed,
    so they don't need to be calculated again
    """

    def __init__(self, queryset) -> PreComputedEmbeddingVectorStore:
        self.queryset = queryset

    @classmethod
    def from_texts(
        cls: Type[PreComputedEmbeddingVectorStore],
        texts: List[str],
        embedding: Any,
        metadatas: Optional[List[dict]] = None,
        **kwargs: Any,
    ) -> PreComputedEmbeddingVectorStore:
        pass

    def add_texts(
        self,
        texts: Iterable[str],
        metadatas: Optional[List[dict]] = None,
        ids: Optional[List[str]] = None,
        **kwargs: Any,
    ) -> List[str]:
        pass

    def similarity_search(
        self,
        query: str,
        k: int = 4,
        filter: Optional[dict] = None,
        **kwargs: Any,
    ) -> List[Document]:
        return [Document(page_content=get_text_to_embed(i)) for i in self.queryset]

import logging

import tiktoken
from bs4 import BeautifulSoup
from numpy import array, average
from sentence_transformers import SentenceTransformer

from .models import TettraPage

TEXT_EMBEDDING_CHUNK_SIZE = 256

logger = logging.getLogger(__name__)


def generate_vector_embeddings(tettra_page: TettraPage):
    text = get_text_to_embed(tettra_page=tettra_page)
    tettra_page.embedding = get_embedding(text)
    tettra_page.save()


def get_embedding(text):
    """Return a list of tuples (text_chunk, embedding) and an average embedding for a text."""
    tokenizer = tiktoken.get_encoding("cl100k_base")
    token_chunks = list(split_into_chunks(text, TEXT_EMBEDDING_CHUNK_SIZE, tokenizer))
    text_chunks = [tokenizer.decode(chunk) for chunk in token_chunks]

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
    model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
    return model.encode(text_array, show_progress_bar=False)


def get_col_average_from_list_of_lists(list_of_lists):
    """Return the average of each column in a list of lists."""
    if len(list_of_lists) == 1:
        return list_of_lists[0]
    else:
        list_of_lists_array = array(list_of_lists)
        average_embedding = average(list_of_lists_array, axis=0)
        return average_embedding.tolist()


# Split a text into smaller chunks of size n, preferably ending at the end of a sentence
def split_into_chunks(text, n, tokenizer):
    tokens = tokenizer.encode(text)
    """Yield successive n-sized chunks from text."""
    i = 0
    while i < len(tokens):
        # Find the nearest end of sentence within a range of 0.5 * n and 1.5 * n tokens
        j = min(i + int(1.5 * n), len(tokens))
        while j > i + int(0.5 * n):
            # Decode the tokens and check for full stop or newline
            chunk = tokenizer.decode(tokens[i:j])
            if chunk.endswith(".") or chunk.endswith("\n"):
                break
            j -= 1
        # If no end of sentence found, use n tokens as the chunk size
        if j == i + int(0.5 * n):
            j = min(i + n, len(tokens))
        yield tokens[i:j]
        i = j


def get_text_to_embed(tettra_page: TettraPage):
    soup = BeautifulSoup(tettra_page.html, features="html.parser")
    return f"Title: {tettra_page.page_title} \n\n {soup.get_text()}"

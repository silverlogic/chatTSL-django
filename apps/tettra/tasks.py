from celery import shared_task

from .utils import generate_vector_embeddings as _generate_vector_embeddings


@shared_task
def generate_vector_embeddings(tettra_page: int):
    from .models import TettraPage

    instance = TettraPage.objects.get(id=tettra_page)
    _generate_vector_embeddings(instance)

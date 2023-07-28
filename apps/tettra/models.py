from __future__ import annotations

from django.db import models

from model_utils import FieldTracker
from pgvector.django import VectorField


class TettraPage(models.Model):
    page_id = models.PositiveIntegerField(unique=True, db_index=True)
    page_title = models.CharField(max_length=255)
    owner_id = models.IntegerField()
    owner_name = models.CharField(max_length=255)
    owner_email = models.EmailField()
    url = models.URLField()
    category_id = models.IntegerField()
    category_name = models.CharField(max_length=255)
    subcategory_id = models.IntegerField(null=True, blank=True)
    subcategory_name = models.CharField(max_length=255, null=True, blank=True)
    html = models.TextField()

    tracker = FieldTracker(
        fields=[
            "page_title",
            "html",
        ]
    )

    def save(self, *args, **kwargs):
        from .tasks import generate_vector_embeddings

        if self.subcategory_id is None or self.subcategory_name is None:
            self.subcategory_id = None
            self.subcategory_name = None

        with self.tracker:
            super().save(*args, **kwargs)
            if (
                self.id is None
                or not self.chunks.exists()
                or any([self.tracker.has_changed("page_title"), self.tracker.has_changed("html")])
            ):
                self.chunks.all().delete()
                generate_vector_embeddings.delay(tettra_page=self.id)


class TettraPageChunk(models.Model):
    tettra_page = models.ForeignKey(TettraPage, related_name="chunks", on_delete=models.CASCADE)

    content = models.TextField()
    embedding = VectorField(
        dimensions=384, null=True, blank=True
    )  # the dimension is the size of the vector returned
    # by the model https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2

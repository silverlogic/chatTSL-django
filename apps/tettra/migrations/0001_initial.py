# Generated by Django 3.2.15 on 2023-06-11 18:21

from django.db import migrations, models

import pgvector.django
from pgvector.django import VectorExtension


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        VectorExtension(),
        migrations.CreateModel(
            name="TettraPage",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                ("page_id", models.PositiveIntegerField(db_index=True, unique=True)),
                ("page_title", models.CharField(max_length=255)),
                ("owner_id", models.IntegerField()),
                ("owner_name", models.CharField(max_length=255)),
                ("owner_email", models.EmailField(max_length=254)),
                ("url", models.URLField()),
                ("category_id", models.IntegerField()),
                ("category_name", models.CharField(max_length=255)),
                ("subcategory_id", models.IntegerField()),
                ("subcategory_name", models.CharField(max_length=255)),
                ("html", models.TextField()),
                ("embedding", pgvector.django.VectorField(blank=True, dimensions=384, null=True)),
            ],
        ),
    ]

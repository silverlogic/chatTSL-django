# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-08-04 16:17
from __future__ import unicode_literals

import django.utils.timezone
from django.db import migrations, models

import model_utils.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="SocialAuthAccessTokenCache",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                (
                    "created",
                    model_utils.fields.AutoCreatedField(
                        default=django.utils.timezone.now, editable=False, verbose_name="created"
                    ),
                ),
                (
                    "modified",
                    model_utils.fields.AutoLastModifiedField(
                        default=django.utils.timezone.now, editable=False, verbose_name="modified"
                    ),
                ),
                ("access_token", models.TextField()),
                ("oauth_token", models.TextField(blank=True)),
                ("oauth_verifier", models.TextField(blank=True)),
                ("code", models.TextField(blank=True)),
            ],
            options={"abstract": False},
        )
    ]

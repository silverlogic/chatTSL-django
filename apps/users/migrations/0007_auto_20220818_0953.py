# Generated by Django 3.2.15 on 2022-08-18 09:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0006_auto_20220607_1535"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="username",
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AddField(
            model_name="user",
            name="wallet",
            field=models.CharField(blank=True, max_length=100),
        ),
    ]

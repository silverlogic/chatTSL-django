# Generated by Django 3.2.12 on 2022-06-07 15:35

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Permission",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                ("name", models.CharField(max_length=255, unique=True)),
                ("slug", models.CharField(max_length=255, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name="PermissionGroup",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                ("name", models.CharField(max_length=255, unique=True)),
                (
                    "permissions",
                    models.ManyToManyField(
                        blank=True, related_name="permission_groups", to="permissions.Permission"
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Role",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                ("name", models.CharField(max_length=255, unique=True)),
                ("slug", models.CharField(max_length=255, unique=True)),
                (
                    "exclude_permissions",
                    models.ManyToManyField(
                        blank=True, related_name="excluded_in_roles", to="permissions.Permission"
                    ),
                ),
                (
                    "permission_groups",
                    models.ManyToManyField(
                        blank=True, related_name="roles", to="permissions.PermissionGroup"
                    ),
                ),
                (
                    "permissions",
                    models.ManyToManyField(
                        blank=True, related_name="roles", to="permissions.Permission"
                    ),
                ),
            ],
        ),
    ]

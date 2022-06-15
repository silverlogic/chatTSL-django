from django.db import models

from apps.permissions.utils import get_slug


class Permission(models.Model):
    name = models.CharField(unique=True, max_length=255)
    slug = models.CharField(unique=True, max_length=255)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = get_slug(self.name)
        return super().save(*args, **kwargs)


class PermissionGroup(models.Model):
    name = models.CharField(unique=True, max_length=255)
    permissions = models.ManyToManyField(Permission, related_name="permission_groups", blank=True)

    def __str__(self):
        return self.name


class Role(models.Model):
    name = models.CharField(unique=True, max_length=255)
    slug = models.CharField(unique=True, max_length=255)

    permission_groups = models.ManyToManyField(PermissionGroup, related_name="roles", blank=True)
    permissions = models.ManyToManyField(Permission, related_name="roles", blank=True)
    exclude_permissions = models.ManyToManyField(
        Permission, related_name="excluded_in_roles", blank=True
    )

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = get_slug(self.name)
        return super().save(*args, **kwargs)

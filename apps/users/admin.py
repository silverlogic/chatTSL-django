from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _

from .forms import UserChangeForm, UserCreationForm
from .models import PasswordValidation, User


@admin.register(User)
class UserAdmin(UserAdmin):
    fieldsets = (
        (None, {"fields": ("email", "password", "date_joined", "last_login")}),
        (
            _("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_superuser",
                    "role",
                    "permission_groups",
                    "is_email_verified",
                )
            },
        ),
        (_("Profile"), {"fields": (("first_name", "last_name"), "wallet", "username")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "password1", "password2", "wallet", "username"),
            },
        ),
    )
    form = UserChangeForm
    add_form = UserCreationForm
    list_display = (
        "id",
        "email",
        "first_name",
        "last_name",
        "username",
        "date_joined",
        "is_active",
        "is_superuser",
    )
    list_filter = ("date_joined", "is_superuser", "is_active")
    search_fields = ("first_name", "last_name", "email")
    ordering = ("id",)
    filter_horizontal = ()


@admin.register(PasswordValidation)
class PasswordValidationAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "is_active",
    )

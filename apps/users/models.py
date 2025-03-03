from django.contrib.auth.models import AbstractBaseUser
from django.db import models
from django.db.models import Q
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from model_utils import Choices

from apps.base.models import CaseInsensitiveEmailField
from apps.permissions.models import Permission

from .managers import UserManager


class PermissionsMixin(models.Model):
    """
    A mixin class that adds the fields and methods necessary to support
    Django's Permission model using the ModelBackend.
    """

    is_active = models.BooleanField(
        _("active"),
        default=True,
        help_text=_(
            "Designates whether this user should be treated as active. "
            "Unselect this instead of deleting accounts."
        ),
    )

    is_superuser = models.BooleanField(
        _("superuser status"),
        default=False,
        help_text=_(
            "Designates that this user has all permissions without " "explicitly assigning them."
        ),
    )

    class Meta:
        abstract = True

    def has_perm(self, perm, obj=None):
        """
        Returns True if the user is superadmin and is active
        """
        return self.is_active and self.is_superuser

    def has_perms(self, perm_list, obj=None):
        """
        Returns True if the user is superadmin and is active
        """
        return self.is_active and self.is_superuser

    def has_module_perms(self, app_label):
        """
        Returns True if the user is superadmin and is active
        """
        return self.is_active and self.is_superuser

    @property
    def is_staff(self):
        return self.is_superuser


class User(PermissionsMixin, AbstractBaseUser):
    email = CaseInsensitiveEmailField(unique=True, db_index=True)
    is_email_verified = models.BooleanField(default=False)
    date_joined = models.DateTimeField(_("date joined"), default=timezone.now)

    # Changing email
    new_email = CaseInsensitiveEmailField(blank=True)
    is_new_email_confirmed = models.BooleanField(
        default=False, help_text="Has the user confirmed they want an email change?"
    )

    # Profile
    first_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100, blank=True)

    # Permissions
    role = models.ForeignKey(
        "permissions.Role", related_name="users", blank=True, null=True, on_delete=models.SET_NULL
    )
    permission_groups = models.ManyToManyField(
        "permissions.PermissionGroup", related_name="users", blank=True
    )
    wallet = models.CharField(max_length=100, blank=True)
    username = models.CharField(max_length=100, unique=True, blank=False, null=True)
    objects = UserManager()

    USERNAME_FIELD = "email"

    class Meta:
        verbose_name = _("user")
        verbose_name_plural = _("users")

    def __str__(self):
        return self.get_full_name()

    def get_short_name(self):
        return self.email

    def get_full_name(self):
        return self.email

    @property
    def permissions(self):
        lookup = Q(permission_groups__in=self.permission_groups.all())
        if self.role:
            lookup = (lookup | Q(permission_groups__roles=self.role) | Q(roles=self.role)) & ~Q(
                excluded_in_roles=self.role
            )

        return Permission.objects.filter(lookup).distinct().values_list("slug", flat=True)


class PasswordValidation(models.Model):
    VALIDATORS = Choices(
        (
            "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
            "User Attribute Similarity",
        ),
        ("django.contrib.auth.password_validation.MinimumLengthValidator", "Minimum Length"),
        ("django.contrib.auth.password_validation.CommonPasswordValidator", "Common Password"),
        ("django.contrib.auth.password_validation.NumericPasswordValidator", "Numeric Password"),
        (
            "apps.users.password_validators.MustContainCapitalLetterValidator",
            "Must Contain Capital Letter",
        ),
        (
            "apps.users.password_validators.MustContainSpecialCharacterValidator",
            "Must Contain Special Character",
        ),
    )
    name = models.CharField(max_length=255, choices=VALIDATORS)
    options = models.JSONField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

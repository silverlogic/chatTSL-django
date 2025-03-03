"""
isort:skip_file
"""

from .routers import DefaultRouter

router = DefaultRouter(trailing_slash=False)

# Login / Register
from .login.views import LoginViewSet  # noqa
from .register.views import RegisterViewSet  # noqa
from .social_auth.views import SocialAuthViewSet  # noqa

router.register(r"login", LoginViewSet, basename="login")
router.register(r"register", RegisterViewSet, basename="register")
router.register(r"social-auth", SocialAuthViewSet, basename="social-auth")

# Users
from .users.views import UsersViewSet  # noqa

router.register(r"users", UsersViewSet, basename="users")

# Forgot Password
from .forgot_password.views import ForgotPasswordViewSet, ResetPasswordViewSet  # noqa

router.register(r"forgot-password", ForgotPasswordViewSet, basename="forgot-password")
router.register(r"forgot-password/reset", ResetPasswordViewSet, basename="reset-password")

# Change Email
from .change_email.views import ChangeEmailViewSet  # noqa

router.register(r"change-email", ChangeEmailViewSet, basename="change-email")

# Tettra
from .tettra.views import (  # noqa
    TettraPageImportDumpViewSet,
    TettraPageCategoriesViewSet,
    TettraPageSubcategoriesViewSet,
)

router.register(r"tettra/import-dump", TettraPageImportDumpViewSet, basename="tettra-import-dump")
router.register(r"tettra/categories", TettraPageCategoriesViewSet, basename="tettra-categories")
router.register(
    r"tettra/subcategories", TettraPageSubcategoriesViewSet, basename="tettra-subcategories"
)

# Chatbot
from .chatbot.views import OpenAIChatViewSet, OpenAIChatMessageViewSet  # noqa

router.register(r"chatbot/open-ai", OpenAIChatViewSet, basename="chatbot-open-ai")
router.register(
    r"chatbot/open-ai-messages", OpenAIChatMessageViewSet, basename="chatbot-open-ai-messages"
)

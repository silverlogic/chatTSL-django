import json

import factory.faker
import factory.fuzzy
import faker
from faker.providers import internet, lorem

from apps.chatbot.models import OpenAIChat, OpenAIChatMessage
from apps.tettra.models import TettraPage, TettraPageCategory, TettraPageSubcategory

faker = faker.Faker()
faker.add_provider(internet)
faker.add_provider(lorem)


class UserFactory(factory.django.DjangoModelFactory):
    email = factory.Faker("email")
    password = factory.PostGenerationMethodCall("set_password", "default")
    username = factory.Faker("user_name")

    class Meta:
        model = "users.User"

    @factory.post_generation
    def permission_groups(self, create, extracted, **kwargs):
        if create and extracted:
            self.permission_groups.add(*extracted)


class PasswordValidationFactory(factory.django.DjangoModelFactory):
    name = "apps.users.password_validators.MustContainSpecialCharacterValidator"

    class Meta:
        model = "users.PasswordValidation"


class TokenFactory(factory.django.DjangoModelFactory):
    user = factory.SubFactory("tests.factories.UserFactory")

    class Meta:
        model = "authtoken.Token"


class PermissionFactory(factory.django.DjangoModelFactory):
    name = factory.Faker("bs")

    class Meta:
        model = "permissions.Permission"


class PermissionGroupFactory(factory.django.DjangoModelFactory):
    name = factory.Faker("company")

    class Meta:
        model = "permissions.PermissionGroup"

    @factory.post_generation
    def permissions(self, create, extracted, **kwargs):
        if create and extracted:
            self.permissions.add(*extracted)


class RoleFactory(factory.django.DjangoModelFactory):
    name = factory.Faker("job")

    class Meta:
        model = "permissions.Role"

    @factory.post_generation
    def permissions(self, create, extracted, **kwargs):
        if create and extracted:
            self.permissions.add(*extracted)

    @factory.post_generation
    def permission_groups(self, create, extracted, **kwargs):
        if create and extracted:
            self.permission_groups.add(*extracted)

    @factory.post_generation
    def exclude_permissions(self, create, extracted, **kwargs):
        if create and extracted:
            self.exclude_permissions.add(*extracted)


class TettraPageFactory(factory.django.DjangoModelFactory):
    page_id = factory.LazyFunction(TettraPage.objects.all().count)
    page_title = factory.Faker("text")
    owner_id = factory.fuzzy.FuzzyInteger(1, 5)
    owner_name = factory.Faker("name")
    owner_email = factory.Faker("email")
    url = faker.url()
    category = factory.SubFactory("tests.factories.TettraPageCategoryFactory")
    subcategory = factory.SubFactory("tests.factories.TettraPageSubcategoryFactory")
    html = factory.LazyFunction(lambda: "<p>Content</p>")

    class Meta:
        model = "tettra.TettraPage"


class TettraPageCategoryFactory(factory.django.DjangoModelFactory):
    category_id = factory.LazyFunction(lambda: TettraPageCategory.objects.count() + 1)
    category_name = factory.Faker("name")

    class Meta:
        model = "tettra.TettraPageCategory"


class TettraPageSubcategoryFactory(factory.django.DjangoModelFactory):
    subcategory_id = factory.LazyFunction(lambda: TettraPageSubcategory.objects.count() + 1)
    subcategory_name = factory.Faker("name")

    class Meta:
        model = "tettra.TettraPageSubcategory"


class TettraPageChunkFactory(factory.django.DjangoModelFactory):
    tettra_page = factory.SubFactory(TettraPageFactory)
    content = factory.fuzzy.FuzzyText()

    class Meta:
        model = "tettra.TettraPageChunk"


class OpenAIChatFactory(factory.django.DjangoModelFactory):
    user = factory.SubFactory(UserFactory)
    model = factory.Faker("random_element", elements=[x[0] for x in OpenAIChat.MODELS])

    class Meta:
        model = "chatbot.OpenAIChat"


class OpenAIChatMessageFactory(factory.django.DjangoModelFactory):
    chat = factory.SubFactory(OpenAIChatFactory)
    role = factory.Faker("random_element", elements=[x[0] for x in OpenAIChatMessage.ROLES])
    content = faker.paragraphs(nb=5)

    class Meta:
        model = "chatbot.OpenAIChatMessage"


class JSONFactory(factory.DictFactory):
    """
    Use with factory.Dict to make JSON strings.
    """

    @classmethod
    def _generate(cls, create, attrs):
        obj = super()._generate(create, attrs)
        return json.dumps(obj)


class SlackInstallationFactory(factory.django.DjangoModelFactory):
    slack_oauth_response = factory.Dict(
        {
            "access_token": "xoxb-TEST",
            "app_id": "TEST643TEST",
            "authed_user": {"id": "TESTLTEST"},
            "bot_user_id": "TESTV7FTEST",
            "enterprise": None,
            "incoming_webhook": {
                "channel": "#slack-sandbox",
                "channel_id": "TEST69NTEST",
                "configuration_url": "https://silverlogic.slack.com/services/TESTUQETEST",
                "url": "https://hooks.slack.com/services/TEST0TEST/TESTUQETEST/TESTRkXN5HX78NXCc4LTTEST",
            },
            "is_enterprise_install": False,
            "ok": True,
            "scope": "incoming-webhook,chat:write.public,chat:write,commands,users.profile:read",
            "team": {"id": "TEST0TEST", "name": "SilverLogic"},
            "token_type": "bot",
        },
        dict_factory=JSONFactory,
    )

    class Meta:
        model = "slack.SlackInstallation"


class SlackEventCallbackDataFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "slack.SlackEventCallbackData"


class SlackOpenAIChatFactory(factory.django.DjangoModelFactory):
    celery_task_id = None
    chat = factory.SubFactory("tests.factories.OpenAIChatFactory")
    slack_event_json = None

    class Meta:
        model = "slack.SlackOpenAIChat"

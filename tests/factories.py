import factory.faker
import factory.fuzzy
import faker
from faker.providers import internet, lorem

from apps.chatbot.models import OpenAIChat, OpenAIChatMessage
from apps.tettra.models import TettraPage, TettraPageCategory, TettraPageSubcategory

faker = faker.Faker()
faker.add_provider(internet)
faker.add_provider(lorem)


class UserFactory(factory.DjangoModelFactory):
    email = factory.Faker("email")
    password = factory.PostGenerationMethodCall("set_password", "default")
    username = factory.Faker("user_name")

    class Meta:
        model = "users.User"

    @factory.post_generation
    def permission_groups(self, create, extracted, **kwargs):
        if create and extracted:
            self.permission_groups.add(*extracted)


class PasswordValidationFactory(factory.DjangoModelFactory):
    name = "apps.users.password_validators.MustContainSpecialCharacterValidator"

    class Meta:
        model = "users.PasswordValidation"


class TokenFactory(factory.DjangoModelFactory):
    user = factory.SubFactory("tests.factories.UserFactory")

    class Meta:
        model = "authtoken.Token"


class PermissionFactory(factory.DjangoModelFactory):
    name = factory.Faker("bs")

    class Meta:
        model = "permissions.Permission"


class PermissionGroupFactory(factory.DjangoModelFactory):
    name = factory.Faker("company")

    class Meta:
        model = "permissions.PermissionGroup"

    @factory.post_generation
    def permissions(self, create, extracted, **kwargs):
        if create and extracted:
            self.permissions.add(*extracted)


class RoleFactory(factory.DjangoModelFactory):
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


class TettraPageFactory(factory.DjangoModelFactory):
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


class TettraPageCategoryFactory(factory.DjangoModelFactory):
    category_id = factory.LazyFunction(lambda: TettraPageCategory.objects.count() + 1)
    category_name = factory.Faker("name")

    class Meta:
        model = "tettra.TettraPageCategory"


class TettraPageSubcategoryFactory(factory.DjangoModelFactory):
    subcategory_id = factory.LazyFunction(lambda: TettraPageSubcategory.objects.count() + 1)
    subcategory_name = factory.Faker("name")

    class Meta:
        model = "tettra.TettraPageSubcategory"


class TettraPageChunkFactory(factory.DjangoModelFactory):
    tettra_page = factory.SubFactory(TettraPageFactory)
    content = factory.fuzzy.FuzzyText()

    class Meta:
        model = "tettra.TettraPageChunk"


class OpenAIChatFactory(factory.DjangoModelFactory):
    user = factory.SubFactory(UserFactory)
    model = factory.Faker("random_element", elements=[x[0] for x in OpenAIChat.MODELS])

    class Meta:
        model = "chatbot.OpenAIChat"


class OpenAIChatMessageFactory(factory.DjangoModelFactory):
    chat = factory.SubFactory(OpenAIChatFactory)
    role = factory.Faker("random_element", elements=[x[0] for x in OpenAIChatMessage.ROLES])
    content = faker.paragraphs(nb=5)

    class Meta:
        model = "chatbot.OpenAIChatMessage"

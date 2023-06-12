import factory.faker
import factory.fuzzy
import faker
from faker.providers import internet

from apps.tettra.models import TettraPage

url_faker = faker.Faker()
url_faker.add_provider(internet)


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
    user = factory.SubFactory(UserFactory)

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
    url = url_faker.url()
    category_id = factory.fuzzy.FuzzyInteger(1, 5)
    category_name = factory.Faker("name")
    subcategory_id = factory.fuzzy.FuzzyInteger(1, 5)
    subcategory_name = factory.Faker("name")
    html = factory.LazyFunction(lambda: "<p>Content</p>")

    class Meta:
        model = "tettra.TettraPage"

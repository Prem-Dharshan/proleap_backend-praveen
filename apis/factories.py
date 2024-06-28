from random import randint
from factory.django import DjangoModelFactory
from factory import LazyFunction, LazyAttribute, SubFactory, post_generation
from factory.faker import Faker
from .models import Status, User, Role, Batch, UserBatch
from datetime import datetime, timedelta

class UserFactory(DjangoModelFactory):
    class Meta:
        model = User

    email = Faker("email")
    username = Faker("user_name")
    name = Faker("name")
    role = Faker("random_element", elements=[Role.USER])
    gender = Faker("random_element", elements=['Male', 'Female', 'Other'])
    phoneNumber = Faker("numerify", text="##########")

    is_active = True
    is_verified = False
    is_staff = False

    created_at = Faker('date_time_this_year')
    updated_at = Faker('date_time_this_year')

    @post_generation
    def password(self, create, extracted, **kwargs):
        self.set_password('proleap')
        if extracted:
            self.set_password(extracted)


class BatchFactory(DjangoModelFactory):
    class Meta:
        model = Batch

    name = Faker('company')
    year = LazyFunction(lambda: datetime.now().year)
    start_time = Faker('date_time_this_year')
    end_time = LazyAttribute(lambda obj: obj.start_time + timedelta(days=randint(1, 3)))
    total_activities = LazyAttribute(2)

    created_at = Faker('date_time_this_year')
    updated_at = Faker('date_time_this_year')

    is_active = True

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        organizer = UserFactory(role=Role.ORGANIZER)
        kwargs['organizer'] = organizer
        return super()._create(model_class, *args, **kwargs)


class UserBatchFactory(DjangoModelFactory):
    class Meta:
        model = UserBatch

    user = SubFactory(UserFactory) 
    batch = SubFactory(BatchFactory)

    completed_activities = 0
    status = Faker('random_element', elements=[Status.NOT_ATTEMPTED])

    created_at = Faker('date_time_this_year')
    updated_at = Faker('date_time_this_year')

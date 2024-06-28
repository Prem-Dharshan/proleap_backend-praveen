from django.core.management.base import BaseCommand
from random import shuffle
from apis.factories import UserFactory, BatchFactory, UserBatchFactory


class Command(BaseCommand):
    help = 'Populate database with users and assign them to batches'

    def handle(self, *args, **kwargs):

        # Create admin user
        UserFactory(email='admin1@proleap.com', username='admin1', is_staff=True, is_superuser=True, password='proleap')
 
        # Create 40 new users
        users = UserFactory.create_batch(40)

        # Create new batches
        batch1 = BatchFactory()
        batch2 = BatchFactory()

        # Shuffle users to evenly distribute them between batches
        shuffle(users)

        # Assign users to batches
        # Assign users to batches
        for index, user in enumerate(users[:20]):
            UserBatchFactory(user=user, batch=batch1)

        for index, user in enumerate(users[20:40]):
            UserBatchFactory(user=user, batch=batch2)

        self.stdout.write(self.style.SUCCESS('Successfully populated database with users and assigned them to batches'))
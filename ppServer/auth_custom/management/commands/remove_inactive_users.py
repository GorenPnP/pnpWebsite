from datetime import datetime, timedelta
from django.utils.timezone import now

from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User


class Command(BaseCommand):
    help = "Removes all users having is_active == False with a buffer of 2 days"

    def handle(self, *args, **options):
        joined = datetime.now() - timedelta(days=2)
        users = User.objects.filter(is_active=False, date_joined__lte=joined)
        self.stdout.write(
            self.style.NOTICE(f'Will delete {users.count()} users: {", ".join([user.username for user in users])}')
        )

        users.delete()
        self.stdout.write(
            self.style.SUCCESS('Successfully removed users')
        )
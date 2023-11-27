import requests
from datetime import datetime, timedelta
from django.utils.timezone import now

from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User


class Command(BaseCommand):
    help = "imports all monsters, their attacks & types from pnp.eu.pythonanywhere.com into the db"

    def handle(self, *args, **options):
        print(requests.get("https://pnp.eu.pythonanywhere.com").__dict__)
        self.stdout.write(
            self.style.SUCCESS('Successfully removed users')
        )
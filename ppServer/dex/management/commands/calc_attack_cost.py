from math import floor
from django.core.management.base import BaseCommand

from dex.models import Attacke



class Command(BaseCommand):
    help = "calculates the cost of every attack based on avg. damage and effect"

    def handle(self, *args, **options):

        attacks = []
        for attack in Attacke.objects.prefetch_related("damage").all():
            cost = 1 if attack.macht_effekt else 0
            cost = sum([cost, *[floor((amount * (int(type.replace("W", ""))+1)) / 8) for amount, type in attack.damage.all().values_list("amount", "type")]])
            attack.cost = min(cost, 7)
            attacks.append(attack)
        Attacke.objects.bulk_update(attacks, fields=["cost"])

        self.stdout.write(self.style.SUCCESS(f'Successfully calculated toe cost of {len(attacks)} Attacks'))

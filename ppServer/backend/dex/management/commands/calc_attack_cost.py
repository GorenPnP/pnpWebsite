from math import floor
from django.core.management.base import BaseCommand

from dex.monster.models import Attacke


def cost_estimate(attack: Attacke) -> int:
    cost = 1 if attack.macht_effekt else 0
    cost = sum([cost, *[floor((d.amount * (int(d.type.replace("W", ""))+1)) / 8) for d in attack.damage.all()]])
    return min(cost, 7)

class Command(BaseCommand):
    help = "calculates the cost of every attack based on avg. damage and effect"

    def handle(self, *args, **options):

        attacks = []
        for attack in Attacke.objects.prefetch_related("damage").all():
            attack.cost = cost_estimate(attack)
            attacks.append(attack)
        Attacke.objects.bulk_update(attacks, fields=["cost"])

        self.stdout.write(self.style.SUCCESS(f'Successfully calculated toe cost of {len(attacks)} Attacks'))

from random import sample

from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import *


@receiver(post_save, sender=SpielerMonster)
def add_stats_to_spielermonster(sender, **kwargs):
    if kwargs['created']:
        instance = kwargs['instance']

        # create stats & get skilled
        skilled_at_indices = sample(range(len(RangStat.StatType)), RangStat.AMOUNT_SKILLED)
        for i, (stat, _) in enumerate(RangStat.StatType):
            obj, _ = RangStat.objects.get_or_create(stat=stat, spielermonster=instance)
            if i in skilled_at_indices:
                obj.skilled = True
                obj.save()

        # rank-up :)
        for _ in range(instance.rang):
            instance.level_up()

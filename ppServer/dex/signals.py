from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import *


@receiver(post_save, sender=SpielerMonster)
def add_stats_to_spielermonster(sender, **kwargs):
    if kwargs['created']:
        instance = kwargs['instance']

        for stat, _ in RangStat.StatType:
            RangStat.objects.get_or_create(stat=stat, spielermonster=instance)

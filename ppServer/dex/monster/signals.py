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
                obj.save(update_fields=["skilled"])

        # rank-up stats :)
        for _ in range(instance.rang): instance.level_up()

        # .. attackenpunkte
        instance.attackenpunkte = sum(MonsterRang.objects.filter(rang__lte=instance.rang).values_list("attackenpunkte", flat=True))
        instance.save(update_fields=["attackenpunkte"])

        # assign random attacks
        attacks = Attacke.objects.exclude(draft=True).filter(cost=0, types__in=[Typ.objects.get(name="Normal").id, *instance.monster.types.all().values_list("id", flat=True)])
        instance.attacken.add(*sample(list(attacks.values_list("id", flat=True)), 2))
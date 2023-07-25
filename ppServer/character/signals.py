from django.contrib.auth.models import User
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from .models import *


@receiver(post_save, sender=User)
def create_spieler(sender, **qwargs):
    if qwargs['created']:
        Spieler.objects.get_or_create(name=qwargs['instance'].username)


@receiver(post_delete, sender=User)
def delete_spieler(sender, **qwargs):
    spieler = Spieler.objects.filter(name=qwargs['instance'].username)
    for s in spieler:
        s.delete()


@receiver(post_save, sender=Gfs)
def init_gfs(sender, **kwargs):
    instance = kwargs['instance']

    for a in Attribut.objects.all():
        GfsAttribut.objects.get_or_create(gfs=instance, attribut=a)

    for f in Fertigkeit.objects.all():
        GfsFertigkeit.objects.get_or_create(gfs=instance, fertigkeit=f)

    for basis in GfsStufenplanBase.objects.all():
        GfsStufenplan.objects.get_or_create(gfs=instance, basis=basis)

    for sk in SkilltreeBase.objects.filter(kind="g"):
        SkilltreeEntryGfs.objects.get_or_create(context=sk, gfs=instance)


@receiver(post_save, sender=Charakter)
def init_character(sender, **kwargs):
    instance = kwargs['instance']

    for a in Attribut.objects.all():
        RelAttribut.objects.get_or_create(char=instance, attribut=a)

    for f in Fertigkeit.objects.all():
        RelFertigkeit.objects.get_or_create(char=instance, fertigkeit=f)




@receiver(post_save, sender=Attribut)
def add_attr(sender, **kwargs):
    if kwargs['created']:
        instance = kwargs['instance']

        for char in Charakter.objects.all():
            RelAttribut.objects.get_or_create(char=char, attribut=instance)

        for gfs in Gfs.objects.all():
            GfsAttribut.objects.get_or_create(gfs=gfs, attribut=instance)


@receiver(post_save, sender=Fertigkeit)
def add_fert(sender, **kwargs):
    if kwargs['created']:
        instance = kwargs['instance']

        for char in Charakter.objects.all():
            RelFertigkeit.objects.get_or_create(char=char, fertigkeit=instance)

        for gfs in Gfs.objects.all():
            GfsFertigkeit.objects.get_or_create(gfs=gfs, fertigkeit=instance)

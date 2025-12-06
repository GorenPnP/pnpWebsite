from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import *

User = get_user_model()


@receiver(post_save, sender=User)
def create_spieler(created: bool, instance, **kwargs):
    if created:
        Spieler.objects.get_or_create(user=instance)

@receiver(post_save, sender=Gfs)
def init_gfs(sender, instance: Gfs, **kwargs):

    for a in Attribut.objects.all():
        GfsAttribut.objects.get_or_create(gfs=instance, attribut=a)

    for f in Fertigkeit.objects.all():
        GfsFertigkeit.objects.get_or_create(gfs=instance, fertigkeit=f)

    for basis in GfsStufenplanBase.objects.all():
        GfsStufenplan.objects.get_or_create(gfs=instance, basis=basis)


@receiver(post_save, sender=Charakter)
def init_character(sender, instance: Charakter, created: bool, **kwargs):
    if created and "creation" in instance.processing_notes and "nachgetragen" in instance.processing_notes["creation"]: return

    RelAttribut.objects.bulk_create([
        RelAttribut(char=instance, attribut=a) for a in Attribut.objects.exclude(relattribut__char=instance)
    ])

    RelFertigkeit.objects.bulk_create([
        RelFertigkeit(char=instance, fertigkeit=a) for a in Fertigkeit.objects.exclude(relfertigkeit__char=instance)
    ])

    existing_groups = RelGruppe.objects.filter(char=instance).values_list("gruppe", flat=True)
    RelGruppe.objects.bulk_create([
        RelGruppe(char=instance, gruppe=token) for token, _ in enums.gruppen_enum if token not in existing_groups
    ])



@receiver(post_save, sender=Attribut)
def add_attr(sender, created: bool, instance: Attribut, **kwargs):
    if created:
        for char in Charakter.objects.all():
            RelAttribut.objects.get_or_create(char=char, attribut=instance)

        for gfs in Gfs.objects.all():
            GfsAttribut.objects.get_or_create(gfs=gfs, attribut=instance)


@receiver(post_save, sender=Fertigkeit)
def add_fert(sender, created: bool, instance: Fertigkeit, **kwargs):
    if created:
        for char in Charakter.objects.all():
            RelFertigkeit.objects.get_or_create(char=char, fertigkeit=instance)

        for gfs in Gfs.objects.all():
            GfsFertigkeit.objects.get_or_create(gfs=gfs, fertigkeit=instance)

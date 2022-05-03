import math

from django.db.models.signals import post_save
from django.dispatch import receiver

from character.models import *
from .models import *


# trigger to post_save: add attribute und fertigkeiten
@receiver(post_save, sender=NewCharakter)
def change_fert(sender, **kwargs):
    if not kwargs['created']:
        instance = kwargs['instance']
        character = instance

        if not NewCharakterFertigkeit.objects.filter(char=character).exists():
            for f in Fertigkeit.objects.all():
                NewCharakterFertigkeit.objects.get_or_create(char=character, fertigkeit=f)

        if not NewCharakterAttribut.objects.filter(char=character).exists():
            for a in Attribut.objects.all():
                NewCharakterAttribut.objects.get_or_create(char=character, attribut=a)


# collect data from gfs & spezies for new_char
# if in LARP, this would only be ferts
@receiver(post_save, sender=NewCharakter)
def collect_data(sender, **kwargs):
    instance = kwargs['instance']
    if kwargs['created']:
        new_char = instance
        gfs = instance.gfs
        wesen = gfs.wesen

        # Attributwerte + maxima
        for attr in Attribut.objects.all():

            # create attr
            relAttr, created = NewCharakterAttribut.objects.get_or_create(char=new_char, attribut=attr)

            if not new_char.larp:
                # set gfs vals
                gfsAttr = get_object_or_404(GfsAttribut, gfs=gfs, attribut=attr)
                relAttr.aktuellerWert = gfsAttr.aktuellerWert
                relAttr.maxWert = gfsAttr.maxWert

                # save
                relAttr.save()

        # fp-bonus
        for fert in Fertigkeit.objects.all():

            relFert, created = NewCharakterFertigkeit.objects.get_or_create(char=new_char, fertigkeit=fert)
            gfsFert = get_object_or_404(GfsFertigkeit, gfs=gfs, fertigkeit=fert)

            relFert.fp_bonus = gfsFert.fp
            relFert.save()

        if not new_char.larp:
            for m in GfsVorteil.objects.filter(gfs=gfs):
                NewCharakterVorteil.objects.get_or_create(char=new_char, teil=m.teil)

            for m in GfsNachteil.objects.filter(gfs=gfs):
                NewCharakterNachteil.objects.get_or_create(char=new_char, teil=m.teil)


# trigger to post_save: add gfs characterization on creation of gfs
@receiver(post_save, sender=Gfs)
def change_fert(sender, **kwargs):
    if kwargs['created']:
        GfsCharacterization.objects.create(gfs=kwargs["instance"])
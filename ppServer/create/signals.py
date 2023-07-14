from django.db.models.signals import post_save
from django.dispatch import receiver

from character.models import *
from .models import *


# trigger to post_save: add gfs characterization on creation of gfs
@receiver(post_save, sender=Gfs)
def change_fert(sender, **kwargs):
    if kwargs['created']:
        GfsCharacterization.objects.create(gfs=kwargs["instance"])
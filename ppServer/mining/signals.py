from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import *

@receiver(post_save, sender=Region)
def add_layers_on_create(sender, instance, **kwargs):
    if kwargs['created']:
        Layer.objects.create(region=instance, index=0, name="Character", is_collidable=False, is_breakable=False)
        Layer.objects.create(region=instance, index=1, name="Blocks", is_collidable=True, is_breakable=True)
        Layer.objects.create(region=instance, index=2, name="Decorations", is_collidable=False, is_breakable=True)
        Layer.objects.create(region=instance, index=3, name="Weather", is_collidable=False, is_breakable=False)

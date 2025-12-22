from django.db.models import Max
from django.db.models.signals import pre_save
from django.dispatch import receiver

from .models import Page


# set default number for pages on page creation
@receiver(pre_save, sender=Page)
def set_to_last_number_on_create(sender, instance, **kwargs):
    # shouldn't ever happen OR on update
    if not instance or instance.pk: return

    instance.number = Page.objects.filter(einheit=instance.einheit).aggregate(nr=Max("number", default=0))["nr"] +1

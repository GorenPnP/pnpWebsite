from django.db.models import Q
from django.db.models.signals import pre_save, post_save, pre_delete, post_delete
from django.dispatch import receiver

from .models import Card

@receiver(pre_delete, sender=Card)
def delete_transactions_when_deleting_card(sender, instance, **kwargs):
    ''' delete transactions that will be sender = receiver = None, therefore will get invalid '''

    instance.get_transactions().filter(Q(sender=None) | Q(receiver=None)).delete()
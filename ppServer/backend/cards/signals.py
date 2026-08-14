from django.db.models import Q
from django.db.models.signals import pre_delete
from django.dispatch import receiver

from character.models import Charakter
from .models import Card

# If a Charakter is going to be deleted, all active RelEffects have a Signal to deactivate their effects.
# If one adds a Transaction with either sender or receiver None (the other the char), the Transaction will
# stay and induce a db constraint exception, because both fields are not allowed to be None at the same time.
# Solution: trigger deactivation manually and delete Transactions afterwards to force the correct order of things.
@receiver(pre_delete, sender=Charakter)
def deactivate_releffects_before_deleting_card_of_char(sender, instance, **kwargs):
    if hasattr(instance, "card"):
        # update wertaenderung on all related, active RelEffects. Set it to 0 ^= no change, because
        # on deletion of an active RelEffect, the applied effect will be deactivated and some calculations take
        # place. Sometimes the result does not comply with the field checks (e.G. negative attribute value) on it.
        instance.releffect_set.filter(is_active=True).exclude(wertaenderung=None).update(wertaenderung=0)

        # deactivate all related RelEffects
        instance.releffect_set.update(is_active=False)

        # cleanup Transactions of the char.card.
        delete_transactions_when_deleting_card(Card, instance.card)


@receiver(pre_delete, sender=Card)
def delete_transactions_when_deleting_card(sender, instance, **kwargs):
    ''' delete transactions that will be sender = receiver = None, therefore will get invalid '''

    instance.get_transactions().filter(Q(sender=None) | Q(receiver=None)).delete()

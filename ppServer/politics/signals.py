from django.contrib.auth.models import User
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from webPush.models import PushSettings, PushTag

from .models import *


@receiver(pre_save, sender=LegalAct)
def send_webpush(sender, instance, **kwargs):

    # on message create or set newly published
    if not instance or not instance.voting_done: return

    old_instance = LegalAct.objects.filter(id=instance.id).first()
    if old_instance and old_instance.voting_done: return

    # notify users
    users = User.objects.all()
    PushSettings.send_message(users, "Neues Gesetzesabstimmung", instance.__str__(), PushTag.politics)


@receiver(post_save, sender=LegalAct)
def create_voters(sender, instance, created, **kwargs):
    if created:
        for politician in Politician.objects.filter(member_of_parliament=True):
            PoliticianVote.objects.get_or_create(politician=politician, legal_act=instance)
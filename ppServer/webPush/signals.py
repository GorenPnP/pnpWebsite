from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import PushSettings


@receiver(post_save, sender=get_user_model())
def create_relQuiz(sender, instance, **kwargs):
    if kwargs['created']:
        PushSettings.objects.get_or_create(user=instance)

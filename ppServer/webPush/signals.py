from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import PushSettings


@receiver(post_save, sender=User)
def create_relQuiz(sender, instance, **kwargs):
    if kwargs['created']:
        PushSettings.objects.get_or_create(user=instance)

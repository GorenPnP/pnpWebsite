import enum, json
from typing import Iterable

from django.contrib.auth.models import User
from django.db import models

from push_notifications.models import WebPushDevice

class PushTag(enum.Enum):
    chat = "chat"
    news = "news"
    quiz = "quiz"
    changelog = "changelog"
    polls = "polls"

    other = None

class PushSettings(models.Model):

    class Meta:
        ordering = ["user"]
        verbose_name = "PushSettings"
        verbose_name_plural = "PushSettings"


    user = models.OneToOneField(User, on_delete=models.CASCADE, unique=True)

    chat = models.BooleanField(default=True)
    news = models.BooleanField(default=True)
    quiz = models.BooleanField(default=True)
    changelog = models.BooleanField(default=True)
    polls = models.BooleanField(default=True)

    def __str__(self):
        return f"PushSettings von {self.user}"


    @classmethod
    def send_message(cls, recipients: Iterable[User], title: str, message: str, tag: PushTag):
        tag = tag.value if type(tag) == PushTag else tag

        # get filtered recipients
        filters = {"user__in": recipients}
        if tag: filters[tag] = True
        users = PushSettings.objects.filter(**filters).values_list("user", flat=True)

        # send message
        msg = {
            "title": title or "",
            "message": message,
            "tag": tag
        }
        return WebPushDevice.objects.filter(user__in=users).send_message(json.dumps(msg))
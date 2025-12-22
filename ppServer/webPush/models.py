import enum, json
from typing import Iterable

from django.contrib.auth import get_user_model
from django.db import models
from django.urls import reverse

from character.models import CustomPermission
from push_notifications.models import WebPushDevice


class PushTag(enum.Enum):
    chat = "chat"
    news = "news"
    quiz = "quiz"
    quiz_control = "quiz-control"
    changelog = "changelog"
    polls = "polls"
    politics = "politics"

    other = None

class PushSettings(models.Model):

    User = get_user_model()

    class Meta:
        ordering = ["user"]
        verbose_name = "PushSettings"
        verbose_name_plural = "PushSettings"


    user = models.OneToOneField(User, on_delete=models.CASCADE, unique=True)

    chat = models.BooleanField(default=True, verbose_name="neue Chat-Nachrichten")
    news = models.BooleanField(default=True, verbose_name="neue Goren-Newsartikel")
    quiz = models.BooleanField(default=True, verbose_name="Änderungen im Quiz")
    changelog = models.BooleanField(default=True, verbose_name="Updates der Website")
    polls = models.BooleanField(default=True, verbose_name="neue Umfragen")
    politics = models.BooleanField(default=True, verbose_name="politische Entscheidungen")

    def __str__(self):
        return f"PushSettings von {self.user}"


    @classmethod
    def send_message(cls, recipients: Iterable[User], title: str, message: str, tag: PushTag):
        # get url to link to when the push message is clicked
        url_map = {
            PushTag.chat: reverse("httpchat:index"),
            PushTag.news: reverse("news:index"),
            PushTag.quiz: reverse("quiz:index"),
            PushTag.quiz_control: reverse("quiz:sp_modules"),
            PushTag.changelog: reverse("changelog:index"),
            PushTag.polls: reverse("base:index"),
            PushTag.politics: reverse("politics:plenum"),

            PushTag.other: None
        }
        url = url_map[tag]

        # transform tag to string
        tag = tag.value if type(tag) == PushTag else tag

        # spielleitung-only tags
        if tag in [PushTag.quiz_control.value]:
            recipients = [user for user in recipients if user.has_perm(CustomPermission.SPIELLEITUNG.value)]

        # get filtered recipients
        filters = {"user__in": recipients}
        if tag and hasattr(PushSettings(), tag): filters[tag] = True
        users = PushSettings.objects.filter(**filters).values_list("user", flat=True)

        # send message
        msg = {
            "title": title or "",
            "message": message,
            "tag": tag,
            "url": url,
        }
        return WebPushDevice.objects.filter(user__in=users).send_message(json.dumps(msg))
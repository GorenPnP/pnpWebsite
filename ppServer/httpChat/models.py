from datetime import datetime, timezone

from django.db import models
from django.utils.text import slugify

from django_resized import ResizedImageField

from markdownfield.models import MarkdownField, RenderedMarkdownField
from markdownfield.validators import VALIDATOR_STANDARD

from character.models import Spieler


class Account(models.Model):
    class Meta:
        ordering = ["spieler", "name"]
        verbose_name = "Person"
        verbose_name_plural = "Personen"
        
    avatar = ResizedImageField(size=[300, 300], upload_to='httpChat/avatar/', crop=['middle', 'center'], null=True, blank=True)

    spieler = models.ForeignKey(Spieler, on_delete=models.SET_NULL, blank=False, null=True)
    name = models.CharField(max_length=200, null=False, blank=False, unique=True)
    slug = models.SlugField(unique=True)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name
    
    def get_avatar_url(self):
        return self.avatar.url if self.avatar else "/static/res/img/goren_logo.png"


def ancient_datetime():
    return datetime(1990, 6, 1, 0, 0, 0, 0, tzinfo=timezone.utc)

class ChatroomAccount(models.Model):
    class Meta:
        verbose_name = "Account"
        verbose_name_plural = "Accounts"

        ordering = ["account", "chatroom"]
        unique_together = ("account", "chatroom")

    chatroom = models.ForeignKey("Chatroom", on_delete=models.CASCADE)
    account = models.ForeignKey(Account, on_delete=models.CASCADE)

    latest_access = models.DateTimeField(default=ancient_datetime)

    def __str__(self):
        return self.account.name


class Chatroom(models.Model):
    class Meta:
        ordering = ["titel"]
        verbose_name = "Chatroom"
        verbose_name_plural = "Chatrooms"

    titel = models.CharField(max_length=200, null=True, blank=True)

    accounts = models.ManyToManyField(Account, through=ChatroomAccount)

    def __str__(self):
        return self.get_titel()
    
    def get_titel(self, excluding_account: Account=None):
        if self.titel: return self.titel

        qs = self.accounts.all()
        if excluding_account:
            qs = qs.exclude(id=excluding_account.id)

        return ", ".join([a.name for a in qs])

    def get_avatar_urls(self, excluding_account: Account=None):
        qs = self.accounts.all()
        
        if excluding_account:
            qs = qs.exclude(id=excluding_account.id)
        return [a.get_avatar_url() for a in qs]

class Message(models.Model):

    class Meta:
        verbose_name = "Nachricht"
        verbose_name_plural = "Nachrichten"

        ordering = ["chatroom", "created_at"]

    choices = [('m', "Message"), ("i", "Info")]

    type = models.CharField(choices=choices, default="m", max_length=1)
    text = models.CharField(max_length=2000)
    # text = MarkdownField(rendered_field='text_rendered', validator=VALIDATOR_STANDARD)
    # text_rendered = RenderedMarkdownField(null=True)
    author = models.ForeignKey(Account, on_delete=models.SET_NULL, null=True, related_name="author")

    chatroom = models.ForeignKey(Chatroom, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "{} (von {})".format(self.text[:47] + (self.text[:47] and "..."), self.author)

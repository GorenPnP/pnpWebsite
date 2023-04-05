from datetime import datetime

from django.db import models
from django.utils.text import slugify

from character.models import Spieler


class Account(models.Model):
    class Meta:
        ordering = ["spieler", "name"]
        verbose_name = "Person"
        verbose_name_plural = "Personen"
        
    # TODO add avatar image

    spieler = models.ForeignKey(Spieler, on_delete=models.SET_NULL, blank=False, null=True)
    name = models.CharField(max_length=200, null=False, blank=False, unique=True)
    slug = models.SlugField(unique=True)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class ChatroomAccount(models.Model):
    class Meta:
        verbose_name = "Account"
        verbose_name_plural = "Accounts"

        ordering = ["account", "chatroom"]
        unique_together = ("account", "chatroom")

    chatroom = models.ForeignKey("Chatroom", on_delete=models.CASCADE)
    account = models.ForeignKey(Account, on_delete=models.CASCADE)

    latest_access = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.account.name

    def set_accessed(self):
        self.update(latest_access = datetime.now())


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

class Message(models.Model):

    class Meta:
        verbose_name = "Nachricht"
        verbose_name_plural = "Nachrichten"

        ordering = ["chatroom", "created_at"]

    choices = [('m', "Message"), ("i", "Info")]

    type = models.CharField(choices=choices, default="m", max_length=1)
    text = models.TextField(default="")
    author = models.ForeignKey(Account, on_delete=models.SET_NULL, null=True)

    chatroom = models.ForeignKey(Chatroom, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "{} (von {})".format(self.text[:47] + (self.text[:47] and "..."), self.author)

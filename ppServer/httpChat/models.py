from django.db import models
from django.utils.text import slugify

from character.models import Spieler


class Account(models.Model):
    class Meta:
        ordering = ["spieler", "name"]
        verbose_name = "Person"
        verbose_name_plural = "Personen"
        

    spieler = models.ForeignKey(Spieler, on_delete=models.SET_NULL, blank=False, null=True)
    name = models.CharField(max_length=200, null=False, blank=False, unique=True)
    slug = models.SlugField(unique=True)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Chatroom(models.Model):
    class Meta:
        ordering = ["titel"]
        verbose_name = "Chatroom"
        verbose_name_plural = "Chatrooms"
        
    titel = models.CharField(max_length=200, null=True, blank=True)

    owners = models.ManyToManyField(Account, related_name="owners")
    admins = models.ManyToManyField(Account, related_name="admins")
    basic_users = models.ManyToManyField(Account, related_name="basic_users")

    def __str__(self):
        return self.titel

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

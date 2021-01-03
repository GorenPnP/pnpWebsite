from django.db import models

from character.models import Spieler


class Message(models.Model):

    class Meta:
        verbose_name = "Nachricht"
        verbose_name_plural = "Nachrichten"

        ordering = ["created_at"]

    text = models.TextField(default="")
    author = models.ForeignKey(Spieler, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "{} ({})".format(self.text[:50], self.author.get_real_name())

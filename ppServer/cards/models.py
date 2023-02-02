import uuid
from django.db import models

from character.models import Spieler


class Card(models.Model):

    class Meta:
        ordering = ['name']
        verbose_name = "NFC-Karte"
        verbose_name_plural = "NFC-Karten"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    card_id = models.PositiveBigIntegerField(null=False, blank=False, unique=True)

    name = models.CharField(max_length=200, default=None, null=True, blank=True)
    spieler = models.ForeignKey(Spieler, on_delete=models.SET_NULL, null=True, blank=True)

    money = models.BigIntegerField(default=0, verbose_name="Guthaben")

    active = models.BooleanField(default=False)

    def __str__(self):
        """ shown e.g. in dropdown as foreign key """
        return self.name

    def get_transactions(self):
        return (Transaction.objects.filter(sender=self) | Transaction.objects.filter(receiver=self)).order_by("-timestamp")

    def __str__(self):
        return self.name


class Transaction(models.Model):

    class Meta:
        ordering = ['-timestamp']
        verbose_name = "Transaktion"
        verbose_name_plural = "Transaktionen"

    sender = models.ForeignKey(Card, related_name="sender", related_query_name="sender", on_delete=models.SET_NULL, null=True, blank=False, verbose_name="Sender")
    receiver = models.ForeignKey(Card, related_name="receiver", related_query_name="receiver", on_delete=models.SET_NULL, null=True, blank=False, verbose_name="Empfänger")

    amount = models.PositiveBigIntegerField(default= 1000, verbose_name="Betrag in Dr.")
    reason = models.TextField(max_length=200, null=False, blank=False, verbose_name="Verwendungszweck")
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "{} Dr. {} -> {}".format(self.amount, self.sender, self.receiver)


class RelCard(models.Model):

    class Meta:
        ordering = ['spieler']

    spieler = models.ForeignKey(Spieler, on_delete=models.CASCADE)
    card = models.ForeignKey(Card, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return "Karte von {}".format(self.spieler)

import uuid
from django.db import models
from django.db.models import Q

from character.models import Spieler, Charakter


class Card(models.Model):

    class Meta:
        ordering = ['name']
        verbose_name = "NFC-Karte"
        verbose_name_plural = "NFC-Karten"

        constraints = [
            # name <> char
            models.CheckConstraint(
                check=(Q(name=None) & ~Q(char=None)) | (~Q(name=None) & Q(char=None)),
                name="either name or char set",
                violation_error_message="Entweder Name oder Charakter muss angegeben sein"
            ),
            # name ++ spieler
            models.CheckConstraint(
                check=(Q(name=None) & Q(spieler=None)) | (~Q(name=None) & ~Q(spieler=None)),
                name="spieler set exactly when name is set",
                violation_error_message="Entweder Charakter oder Name mit Spieler muss angegeben sein"
            ),
            # char has to have active=True
            models.CheckConstraint(
                check=Q(char=None) | Q(active=True),
                name="char's account needs to stay active",
                violation_error_message="Bankaccount eines Charakters muss aktiv sein"
            ),
        ]

    # "bank account"
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    money = models.BigIntegerField(default=0, verbose_name="Guthaben")
    active = models.BooleanField(default=False)

    # optional debit card
    card_id = models.PositiveBigIntegerField(null=True, blank=True, unique=True)
    card_distributed_to_player = models.BooleanField(default=False)

    # "bank account" owner & its player
    name = models.CharField(max_length=200, null=True, blank=True)
    spieler = models.ForeignKey(Spieler, on_delete=models.SET_NULL, null=True, blank=True)
    
    char = models.OneToOneField(Charakter, on_delete=models.CASCADE, null=True, blank=True)

    @property
    def account_owner(self) -> Spieler:
        return self.spieler or self.char.eigentümer

    @property
    def account_name(self):
        return self.name or self.char.name

    def __str__(self):
        """ shown e.g. in dropdown as foreign key """
        return f"{self.account_name} ({self.account_owner})"

    def get_transactions(self):
        return (Transaction.objects.filter(sender=self) | Transaction.objects.filter(receiver=self)).order_by("-timestamp")



class Transaction(models.Model):

    class Meta:
        ordering = ['-timestamp']
        verbose_name = "Transaktion"
        verbose_name_plural = "Transaktionen"
        constraints = [
            # at least one of sender or receiver is set
            models.CheckConstraint(
                check=~Q(sender=None) | ~Q(receiver=None),
                name="at least one of sender or receiver set",
                violation_error_message="Mindestens einer von Sender und Empfänger muss gesetzt sein"
            ),
        ]

    sender = models.ForeignKey(Card, related_name="sender", related_query_name="sender", on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Sender")
    receiver = models.ForeignKey(Card, related_name="receiver", related_query_name="receiver", on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Empfänger")

    amount = models.PositiveBigIntegerField(default=1000, verbose_name="Betrag in Dr.")
    reason = models.TextField(max_length=200, null=False, blank=False, verbose_name="Verwendungszweck")
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "{} Dr. {} -> {}".format(self.amount, self.sender, self.receiver)


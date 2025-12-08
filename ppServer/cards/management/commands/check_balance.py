from django.core.management.base import BaseCommand
from django.db.models import Sum, F, Subquery, OuterRef, Q, Count, Value, PositiveBigIntegerField
from django.db.models.functions import Coalesce

from cards.models import Card, Transaction
from httpChat.models import SumSubquery

class Command(BaseCommand):
    help = "compares current account balance to the transaction history of Characters"

    def handle(self, *args, **options):

        # get imbalanced cards
        cards = [*Card.objects.annotate(
            received = Coalesce(SumSubquery("amount", queryset=Transaction.objects.filter(receiver__pk=OuterRef("pk")), output_field=PositiveBigIntegerField()), Value(0)),
            spent = Coalesce(SumSubquery("amount", queryset=Transaction.objects.filter(sender__pk=OuterRef("pk")), output_field=PositiveBigIntegerField()), Value(0)),

            transaction_balance = F("received") - F("spent"),
            difference = F("money") - F("transaction_balance"),
        ).exclude(char=None).exclude(difference=0)]

        # log results
        if len(cards):
            self.stdout.write(self.style.WARNING(f'{len(cards)} Konten haben ungleichen Kontostand zu Transaktionen:\n'))
            for card in cards:
                self.stdout.write(self.style.WARNING(f'{card}: {card.money} (balance) - {card.transaction_balance} (transactions) = {card.difference} missing in transactions'))
        
        else:
            self.stdout.write(self.style.SUCCESS('alle Konten haben zueinander passende Kontostände und Transaktionen'))

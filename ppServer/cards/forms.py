from django import forms

from .models import Card, Transaction

class AdminTransactionForm(forms.ModelForm):

    class Meta:
        model = Transaction
        fields = ['sender', 'receiver', 'amount', 'reason']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        cards = Card.objects.filter(active=True)

        self.fields['sender'] = forms.ModelChoiceField(
            queryset=cards,
            label="Sender",
            widget=forms.Select(attrs={'class': 'form-control select2'})
        )
        self.fields['receiver'] = forms.ModelChoiceField(
            queryset=cards,
            label="Empfänger",
            widget=forms.Select(attrs={'class': 'form-control select2'})
        )


class SpielerTransactionForm(forms.ModelForm):

    class Meta:
        model = Transaction
        fields = ['receiver', 'amount', 'reason']

    def __init__(self, *args, **kwargs):
        uuid = kwargs.pop('uuid')
        super().__init__(*args, **kwargs)

        cards = Card.objects.filter(active=True).exclude(id=uuid)

        self.fields['receiver'] = forms.ModelChoiceField(
            queryset=cards,
            label="Empfänger",
            widget=forms.Select(attrs={'class': 'form-control select2'})
        )


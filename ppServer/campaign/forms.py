from django import forms
from django.core.validators import MaxValueValidator, MinValueValidator

from character.models import Charakter


class AuswertungForm(forms.Form):

    story = forms.CharField(label="Story", required=True)

    ep = forms.IntegerField(initial=0, label="EP", required=True, min_value=1)
    sp = forms.IntegerField(initial=0, label="SP", required=True)
    rang = forms.IntegerField(initial=0, label="Ränge", required=True)
    prestige = forms.IntegerField(initial=0, label="Prestige", required=True)
    verzehr = forms.IntegerField(initial=0, label="Verzehr", required=True)

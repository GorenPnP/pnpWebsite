from django import forms

from .models import *

class MonsterVisibilityForm(forms.Form):
    monster = forms.ModelMultipleChoiceField(queryset=Monster.objects.all(), widget=forms.CheckboxSelectMultiple(), required=True)
    spieler = forms.ModelMultipleChoiceField(queryset=Spieler.objects.all(), widget=forms.CheckboxSelectMultiple(), required=True)

    visible = forms.BooleanField(label="Sollen Monster für die Spieler sichtbar sein?", initial=True, required=False)
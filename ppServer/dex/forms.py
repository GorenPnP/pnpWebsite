from django import forms
from django.core.exceptions import ValidationError
from django.forms.widgets import Input

from .models import *

class MonsterVisibilityForm(forms.Form):
    monster = forms.ModelMultipleChoiceField(queryset=Monster.objects.all(), widget=forms.CheckboxSelectMultiple(), required=True)
    spieler = forms.ModelMultipleChoiceField(queryset=Spieler.objects.all(), widget=forms.CheckboxSelectMultiple(), required=True)

    visible = forms.BooleanField(label="Sollen Monster für die Spieler sichtbar sein?", initial=True, required=False)


class TeamForm(forms.Form):
    class ColorWidget(Input):
        def __init__(self, attrs=dict()) -> None:
            attrs["type"] = "color"
            super().__init__(attrs)

    name = forms.CharField(max_length=256, required=True)
    farbe = forms.CharField(widget=ColorWidget(), required=True)
    textfarbe = forms.CharField(widget=ColorWidget(), required=True)


class SpielerMonsterForm(forms.ModelForm):
    class Meta:
        model = SpielerMonster
        fields = ["name", "rang"]


class CatchMonsterForm(forms.ModelForm):

    class Meta:
        model = SpielerMonster
        fields = ["monster", "name", "rang"]

    def __init__(self, *args, curr_spieler: Spieler, **kwargs):
        super().__init__(*args, **kwargs)

        # display only visible monsters
        self.curr_spieler = curr_spieler
        self.fields["monster"].queryset = Monster.objects.filter(visible=curr_spieler)


    def clean_monster(self):
        monster = self.cleaned_data["monster"]
        if not monster.visible.filter(id=self.curr_spieler.id).exists():
            raise ValidationError("Das Monster ist dir unbekannt", code="invalid")
        
        return monster

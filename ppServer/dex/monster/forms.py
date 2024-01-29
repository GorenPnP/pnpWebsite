from django import forms
from django.db.models import Count
from django.forms.widgets import Input, CheckboxSelectMultiple

from .models import *

class MonsterVisibilityForm(forms.Form):
    monster = forms.ModelMultipleChoiceField(queryset=Monster.objects.all(), widget=forms.CheckboxSelectMultiple(), required=True)
    spieler = forms.ModelMultipleChoiceField(queryset=Spieler.objects.all(), widget=forms.CheckboxSelectMultiple(), required=True)

    visible = forms.BooleanField(label="Sollen Monster für die Spieler sichtbar sein?", initial=True, required=False)

class AttackToMonsterForm(forms.Form):
    class MonsterSelect(CheckboxSelectMultiple):
        option_template_name = 'dex/sp/select_option_monster.html'
    monster = forms.ModelMultipleChoiceField(queryset=Monster.objects.prefetch_related("types", "attacken").annotate(num_attacken=Count("attacken")).all().order_by("number"), widget=MonsterSelect())
    monster_feddich = forms.BooleanField(required=False)

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

class SpSpielerMonsterForm(forms.ModelForm):
    class Meta:
        model = SpielerMonster
        fields = ["name", "rang"]

    keep_attacks = forms.BooleanField(label="Attacken übernehmen", required=False)

class SpielerMonsterNameForm(forms.ModelForm):
    class Meta:
        model = SpielerMonster
        fields = ["name"]


class ProposeAttackForm(forms.ModelForm):
    class Meta:
        model = Attacke
        fields = [
            "name", "damage", "description", "types", "macht_schaden", "macht_effekt",
            "angriff_nahkampf", "angriff_fernkampf", "angriff_magie", "verteidigung_geistig", "verteidigung_körperlich", "cost"
        ]
        widgets = {
            "damage": forms.CheckboxSelectMultiple(),
            "types": forms.CheckboxSelectMultiple(),
        }

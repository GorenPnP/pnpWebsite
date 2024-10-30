
from django import forms

from character.models import Affektivität, Charakter


class PersonalForm(forms.ModelForm):
    class Meta:
        model = Charakter
        fields = [
            "image",
            "name",
            "persönlichkeit",

            "gewicht",
            "größe",
            "alter",
            "geschlecht",
            "sexualität",
            "beruf",
            "präf_arm",
            "religion",
            "hautfarbe",
            "haarfarbe",
            "augenfarbe",

            "persönlicheZiele",
            "sonstige_items",
            "notizen"
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if kwargs["instance"].larp:
            self.fields['beruf'].widget = forms.HiddenInput()


class AffektivitätForm(forms.ModelForm):
    class Meta:
        model = Affektivität
        fields = ["name", "wert", "notizen"]

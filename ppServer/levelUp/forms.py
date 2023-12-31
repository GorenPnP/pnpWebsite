
from django import forms

from character.models import Charakter
from httpChat.forms import M2MSelect

from character.models import Affektivität


class PersonalForm(forms.ModelForm):
    class Meta:
        model = Charakter
        widgets = {"persönlichkeit": M2MSelect()}
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
            "sonstiges_alchemie",
            "sonstiges_cyberware",
            "notizen"
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        required_fields = ["persönlichkeit"]
        for field in required_fields:
            self.fields[field].required = True

        for field in self.fields.values():
            if field.required:
                field.label += "*" 

        if kwargs["instance"].larp:
            self.fields['beruf'].widget = forms.HiddenInput()


class AffektivitätForm(forms.ModelForm):
    class Meta:
        model = Affektivität
        fields = ["name", "wert", "notizen"]

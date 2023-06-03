
from django import forms

from character.models import Charakter
from httpChat.forms import M2MSelect


class PersonalForm(forms.ModelForm):
    class Meta:
        model = Charakter
        widgets = {"persönlichkeit": M2MSelect()}
        fields = [
            "name",
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

            "persönlichkeit",
            "persönlicheZiele",
            "notizen"
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.fields.values():
            field.required = True

        if kwargs["instance"].larp:
            self.fields['beruf'].widget = forms.HiddenInput()
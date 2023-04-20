
from django import forms

from character.models import Charakter


class EndForm(forms.ModelForm):
    class Meta:
        model = Charakter
        fields = ["name", "beruf", "religion"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['religion'].required = True

        self.fields['beruf'].required = True
        if kwargs["instance"].larp:
            self.fields['beruf'].widget = forms.HiddenInput()
from django import forms

from crispy_forms.layout import Layout, Div, Field, Fieldset

from base.crispy_form_decorator import crispy
from character.models import Affektivität, Charakter

@crispy(form_tag=False)
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

    def get_layout(self):
        return Layout(
            Div(
                Field('image', wrapper_class='col-12 col-sm'),
                Field('name', wrapper_class='col-12 col-sm'),
            css_class='row align-items-center'),
            Fieldset("Aussehen",
                Div(
                    Field('gewicht', wrapper_class='col-12 col-sm'),
                    Field('größe', wrapper_class='col-12 col-sm'),
                    Field('alter', wrapper_class='col-12 col-sm'),
                css_class='row align-items-center'),
                Div(
                    Field('hautfarbe', wrapper_class='col-12 col-sm'),
                    Field('haarfarbe', wrapper_class='col-12 col-sm'),
                    Field('augenfarbe', wrapper_class='col-12 col-sm'),
                css_class='row align-items-center'),
            ),
            Fieldset("innere Werte & Präferenzen",
                Div(
                    Field('geschlecht', wrapper_class='col-12 col-sm'),
                    Field('sexualität', wrapper_class='col-12 col-sm'),
                css_class='row align-items-center'),
                "persönlichkeit",
                "präf_arm",
                "beruf",
                "religion",
            ),
            Fieldset("Ziele & Zukunft",
                "persönlicheZiele",
                "sonstige_items",
                "notizen"
            )
        )


@crispy(form_tag=False)
class AffektivitätForm(forms.ModelForm):
    class Meta:
        model = Affektivität
        fields = ["name", "wert", "notizen"]

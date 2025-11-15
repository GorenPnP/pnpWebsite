from django import forms

from crispy_forms.bootstrap import AppendedText
from crispy_forms.layout import Layout, Div, Field, Fieldset, Submit

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


@crispy(form_tag=False)
class KonzentrationForm(forms.ModelForm):
    class Meta:
        model = Charakter
        fields = ["konzentration"]

    konzentration = forms.IntegerField(initial=0, required=True, help_text="je 2 Konzentration kosten 1 SP", step_size=2)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["konzentration"].widget.attrs["min"] = self.instance.konzentration
        self.fields["konzentration"].min_value = self.instance.konzentration

        # self.helper is coming from @crispy decorator
        self.helper.layout = Layout(
            AppendedText('konzentration', f'aktuell: {self.instance.konzentration or 0}', form="form"),
        )
    
    def clean_konzentration(self):

        if "konzentration" not in self.cleaned_data:
            raise forms.ValidationError("Konzentration ist nicht da")

        konz_aktuell =  self.instance.konzentration or 0
        if self.cleaned_data["konzentration"] < konz_aktuell:
            raise forms.ValidationError("Konzentration kann nicht kleiner werden")

        if (self.cleaned_data["konzentration"] - konz_aktuell) % 2:
            raise forms.ValidationError("Konzentration hat keinen Zuwachs einer geraden Zahl")

        return self.cleaned_data["konzentration"]

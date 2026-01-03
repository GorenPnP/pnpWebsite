from django import forms

from crispy_forms.layout import Layout, Submit, HTML, Fieldset, ButtonHolder, LayoutObject, TEMPLATE_PACK, Div, Field, Button

from base.crispy_form_decorator import crispy
from character.models import Beruf, Religion

@crispy(form_tag=False, extra_inputs=[Submit('submit', 'Speichern'), Button("", "Zurück", css_class="btn btn-outline-light ms-3")])
class BerufForm(forms.ModelForm):
    class Meta:
        model = Beruf
        fields = ["titel", "beschreibung"]
        widgets = {"beschreibung": forms.widgets.Textarea()}


@crispy(form_tag=False, extra_inputs=[Submit('submit', 'Speichern'), Button("", "Zurück", css_class="btn btn-outline-light ms-3", onclick="history.back()")])
class ReligionForm(forms.ModelForm):
    class Meta:
        model = Religion
        fields = ["titel", "beschreibung"]
        widgets = {"beschreibung": forms.widgets.Textarea()}

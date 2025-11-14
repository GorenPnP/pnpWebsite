from django import forms

from crispy_forms.layout import Layout, Div, Field

from base.crispy_form_decorator import crispy
from shop.models import Tinker

@crispy(form_tag=False)
class AddToInventoryForm(forms.Form):
    amount = forms.IntegerField(min_value=1, initial=1, label="Anzahl", required=True)
    item = forms.ModelChoiceField(Tinker.objects.order_by("name"), label="Item")

    def get_layout(self):
        return Layout(
            Div(
                Field('amount', wrapper_class='col-12 col-sm'),
                Field('item', wrapper_class='col-12 col-sm'),
            css_class='row'),
        )
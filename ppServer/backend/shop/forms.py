from django import forms

from crispy_forms.layout import Button, Layout, Div, Field, Submit, Reset, Fieldset
from django_filters import FilterSet

from base.crispy_form_decorator import crispy

from .models import *

class ShopFilter(FilterSet):
    """ adds crispy to django-filter model filter for shop items """
    def get_form_class(self):

        @crispy(form_method="get")
        class Form(super().get_form_class()):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                self.helper.layout = Layout(
                    *self.fields.keys(),
                    Submit('submit', "Filtern", css_class="btn btn-light me-1"),
                    Reset('reset', "Zurücksetzen", css_class="btn btn-outline-light"),
                )
        return Form


def get_ProposeForm(model: BaseShop) -> type[forms.Form]:
    Form = crispy(forms.modelform_factory(model=model, exclude=["firmen", "frei_editierbar", "has_implementation", "minecraft_mod_id", "wooble_buy_price", "wooble_sell_price"]))

    class ModelForm(Form):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.helper.layout = Layout(
                Div(
                    Field('icon', wrapper_class='col-12 col-md-4'),
                    Field('name', wrapper_class='col-12 col-md-8'),
                css_class='row align-items-center'),
                "beschreibung",
                Div(
                    Field('ab_stufe', wrapper_class='col-12 col-sm-3'),
                    Field('stufenabhängig', wrapper_class='col-12 col-sm-3'),
                css_class='row align-items-center'),
                *[field for field in self.fields.keys() if field not in ["icon", "name", "beschreibung", "stufenabhängig", "ab_stufe"]],
                Submit("submit", "Item vorschlagen"),
                Button("", "Zurück", css_class="btn btn-outline-light ms-3", onclick="history.back()")
            )
    return ModelForm
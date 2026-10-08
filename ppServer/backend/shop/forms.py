from datetime import date

from django import forms
from django.apps import apps
from django.core.exceptions import ValidationError

from crispy_forms.layout import Button, Layout, Div, Field, Submit
from django_filters import FilterSet

from base.crispy_form_decorator import crispy
from character.models import CustomPermission, Spieler, Charakter

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
                )
        return Form


def get_ProposeForm(model: BaseShop) -> type[forms.Form]:
    Form = crispy(forms.modelform_factory(model=model, exclude=["frei_editierbar", "has_implementation", "minecraft_mod_id", "wooble_buy_price", "wooble_sell_price"]))

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


def get_BuyForm(spieler: Spieler, item: BaseShop):
    @crispy(form_method="post")
    class Form(forms.Form):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)

            if spieler.user.has_perm(CustomPermission.SPIELLEITUNG.value):
                self.fields["price"] = forms.IntegerField(initial=item.curr_price, min_value=0, required=True, label="Preis in Dr.")
            else:
                self.fields["char"].queryset = self.fields["char"].queryset.prefetch_related("eigentümer__user").filter(eigentümer=spieler)

            if item.stufenabhängig:
                self.fields["stufe"] = forms.IntegerField(initial=1, min_value=1, required=True, label="Item Stufe")

            self.helper.layout = Layout(
                *self.fields.keys(),
                Submit('submit', 'Kaufen', css_class="btn btn-primary"),
            )

        amount = forms.IntegerField(initial=1, min_value=1, required=True, label="Anzahl")
        char = forms.ModelChoiceField(required=True, label="für Charakter", queryset=Charakter.objects.select_related("eigentümer__user").prefetch_related("card").order_by("name"))


        def clean(self):

            # check if character is allowed for spieler
            char = self.cleaned_data.get("char")
            if char.eigentümer != spieler and not spieler.user.has_perm(CustomPermission.SPIELLEITUNG.value):
                self.add_error("char", ValidationError("Keine Erlaubnis einzukaufen"))
                return

            # check if stufe exists
            stufe = self.cleaned_data.get("stufe")
            if item.stufenabhängig and stufe is None:
                self.add_error("stufe", ValidationError("Die Stufe ist nicht angekommen"))
                return

            # check if item is available to buy
            AvailableModel = apps.get_model("character", f"rel{item._meta.model_name}available")
            if not char.in_erstellung and AvailableModel.objects.filter(char=char, item=item, last_tried=date.today()).exists():
                raise ValidationError("Heute kommt keine neue Ware mehr. Versuch's doch morgen nochmal.")

            # cost of purchase
            cost = self.cleaned_data.get("amount") * self.cleaned_data.get("price", item.curr_price or 0) * (stufe or 1)
            if cost > char.geld:
                raise ValidationError("Du bist zu arm dafür")

            return super().clean()

    return Form

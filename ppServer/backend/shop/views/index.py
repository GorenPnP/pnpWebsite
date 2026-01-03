from django import forms

from django.db.models import Model
from django.contrib import messages
from django.http import Http404
from django.shortcuts import render, redirect
from django.urls import reverse

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Field, Layout, Div, Submit, Button

from base.crispy_form_decorator import crispy
from base.views import reviewable_shop
from ppServer.decorators import spielleitung_only, verified_account

from ..models import *
from .list import shopmodel_list


@verified_account
@spielleitung_only()
def review_items(request):

    context = {"topic": "Neue Items", "items": reviewable_shop()}

    if not context["items"]:
        return redirect("base:index")

    return render(request, "shop/review_items.html", context)


@verified_account
@spielleitung_only()
def transfer_items(request):

    @crispy(form_tag=False)
    class TransferForm(forms.Form):
        action_enum = [
            ('Alchemie', 'Drogen zu Alchemie'),
            ('Rune', "'o Grome zu Rituale_Runen"),
            ('Technik', 'Programme zu Ausrüstung_Technik')
        ]
        aktion = forms.ChoiceField(choices=action_enum, required=True)
        items = forms.ModelMultipleChoiceField(Item.objects.all(), widget=forms.CheckboxSelectMultiple(), required=True)

    if request.method == "GET":
        context = {
            "topic": "Item-Transfer",
            "form": TransferForm()
        }

    if request.method == "POST":
        form = TransferForm(request.POST)
        form.full_clean()
        if not form.is_valid():
            messages.error(request, "Transfer konnte nicht durchgeführt werden")
        else:
            fields = ("name", "beschreibung", "icon", "ab_stufe", "illegal", "lizenz_benötigt", "frei_editierbar", "stufenabhängig")

            if form.cleaned_data["aktion"] == "Alchemie":
                Model = Alchemie
                ModelFirma = FirmaAlchemie
                kategorie = 'd'
            if form.cleaned_data["aktion"] == "Rune":
                Model = Rituale_Runen
                kategorie = 'g'
                ModelFirma = FirmaRituale_Runen
            if form.cleaned_data["aktion"] == "Technik":
                Model = Ausrüstung_Technik
                ModelFirma = FirmaAusrüstung_Technik
                kategorie = 'p'

            for item in form.cleaned_data["items"]:

                # create in new category
                values = {field: getattr(item, field) for field in fields}
                values["kategorie"] = kategorie
                new_item, _ = Model.objects.get_or_create(**values)

                # link to firma
                for firmaitem in item.firmaitem_set.all():
                    if form.cleaned_data["aktion"] == "Rune":
                        new_item.frei_editierbar = True
                        new_item.save(update_fields=["frei_editierbar"])
                        ModelFirma.objects.get_or_create(item=new_item, firma=firmaitem.firma, defaults={"stufe_1": firmaitem.preis, "verfügbarkeit": firmaitem.verfügbarkeit})
                    else:
                        ModelFirma.objects.get_or_create(item=new_item, firma=firmaitem.firma, defaults={"preis": firmaitem.preis, "verfügbarkeit": firmaitem.verfügbarkeit})
            names = ", ".join(form.cleaned_data["items"].values_list("name", flat=True))

            # delete old item
            form.cleaned_data["items"].delete()

            messages.success(request, f"{names} zu {form.cleaned_data['aktion']}")

        return redirect(request.build_absolute_uri())

    return render(request, "shop/sp_transfer_from_items.html", context)


@verified_account
def index(request):
    return render(request, "shop/index.html", {
        "topic": "Shop",
        "links": [{"link": reverse(f'shop:{m._meta.model_name}_list'), "text": m._meta.verbose_name_plural} for m in shopmodel_list],
    })


@verified_account
def propose_item(request, model: Model):
    if model not in shopmodel_list: return Http404()

    ModelForm = forms.modelform_factory(model=model, exclude=["firmen", "frei_editierbar", "has_implementation", "minecraft_mod_id", "wooble_buy_price", "wooble_sell_price"])
    form = ModelForm()

    if request.method == 'POST':
        form = ModelForm(request.POST)
        form.full_clean()
        if form.is_valid():
            item = form.save()
            messages.success(request, "Vorschlag wurde eingereicht")
            return redirect(f"shop:{model._meta.model_name}_list")

        messages.error(request, "Beim Speichern sind Fehler aufgetreten")


    form.helper = FormHelper()
    form.helper.layout = Layout(
        Div(
            Field('icon', wrapper_class='col-12 col-md-4'),
            Field('name', wrapper_class='col-12 col-md-8'),
        css_class='row align-items-center'),
        "beschreibung",
        Div(
            Field('ab_stufe', wrapper_class='col-12 col-sm-3'),
            Field('illegal', wrapper_class='col-12 col-sm-3'),
            Field('lizenz_benötigt', wrapper_class='col-12 col-sm-3'),
            Field('stufenabhängig', wrapper_class='col-12 col-sm-3'),
        css_class='row align-items-center'),
        *[field for field in form.fields.keys() if field not in ["icon", "name", "beschreibung", "illegal", "lizenz_benötigt", "stufenabhängig", "ab_stufe"]],
        Submit("submit", "Item vorschlagen"),
        Button("", "Zurück", css_class="btn btn-outline-light ms-3", onclick="history.back()")
    )
    return render(request, "shop/propose.html", {
        "topic": "neues Item",
        "app_index": Model._meta.verbose_name_plural,
        "app_index_url": reverse(f"shop:{Model._meta.model_name}_list"),
        "form": form,
    })

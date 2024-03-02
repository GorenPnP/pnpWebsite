from django import forms

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

from base.views import reviewable_shop
from ppServer.decorators import spielleiter_only, verified_account
from ..models import *


@login_required
@spielleiter_only()
def review_items(request):

    context = {"topic": "Neue Items", "items": reviewable_shop()}

    if not context["items"]:
        return redirect("base:index")

    return render(request, "shop/review_items.html", context)


@login_required
@spielleiter_only()
def transfer_items(request):

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

            print(form.cleaned_data)
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


@login_required
@verified_account
def index(request):
    return render(request, "shop/index.html", {"topic": "Shop"})

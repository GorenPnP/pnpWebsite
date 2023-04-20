from django import forms

from shop.models import Tinker

class AddToInventoryForm(forms.Form):
    amount = forms.IntegerField(min_value=1, initial=1, label="Anzahl", required=True)
    item = forms.ModelChoiceField(Tinker.objects.order_by("name"), label="Item")
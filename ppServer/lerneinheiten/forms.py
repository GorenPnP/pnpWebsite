from django import forms

from .models import *

class EinheitForm(forms.ModelForm):
    class Meta:
        model = Einheit
        fields = ["titel", "fach", "klasse"]


class PageForm(forms.ModelForm):
    class Meta:
        model = Page
        fields = ["titel", "einheit"]

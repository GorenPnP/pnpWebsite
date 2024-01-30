from django import forms
from django.forms.widgets import HiddenInput

from dex.monster import forms as monster_forms

from .models import *

class EinheitForm(forms.ModelForm):
    class Meta:
        model = Einheit
        fields = ["titel", "fach", "klasse"]


class PageForm(forms.ModelForm):
    class Meta:
        model = Page
        fields = ["titel", "einheit", "type"]

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.fields['einheit'].widget = HiddenInput()

class PageUpdateForm(forms.ModelForm):
    class Meta:
        model = Page
        fields = ["titel", "color"]

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.fields['color'].widget = monster_forms.ColorWidget()
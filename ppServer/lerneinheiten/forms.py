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
        fields = ["titel", "color", "content", "solution"]

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.fields['color'].widget = monster_forms.ColorWidget()
        # lerninhalt
        if self.instance.type == "i":
            self.fields['content'].widget = HiddenInput()
            self.fields['solution'].widget = HiddenInput()


class SpielerPageForm(forms.ModelForm):
    class Meta:
        model = SpielerPage
        fields = ["answer"]


class InquiryForm(forms.ModelForm):
    class Meta:
        model = Inquiry
        fields = ["question", "spieler", "page"]

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.fields['spieler'].widget = HiddenInput()
        self.fields['page'].widget = HiddenInput()
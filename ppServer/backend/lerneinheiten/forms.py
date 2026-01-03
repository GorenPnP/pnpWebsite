from django import forms
from django.forms.widgets import HiddenInput

from crispy_forms.layout import Layout, Div, Field

from base.crispy_form_decorator import crispy
from dex.monster import forms as monster_forms

from .models import *

@crispy(form_tag=False)
class EinheitForm(forms.ModelForm):
    class Meta:
        model = Einheit
        fields = ["titel", "fach", "klasse"]

    def get_layout(self):
        return Layout(
            "titel",
            Div(
                Field('fach', wrapper_class='col-12 col-sm-9'),
                Field('klasse', wrapper_class='col-12 col-sm-3'),
            css_class='row'),
        )


@crispy(form_tag=False)
class PageForm(forms.ModelForm):
    class Meta:
        model = Page
        fields = ["titel", "einheit", "type"]

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.fields['einheit'].widget = HiddenInput()


@crispy(form_tag=False)
class PageUpdateForm(forms.ModelForm):
    class Meta:
        model = Page
        fields = ["titel", "color", "content", "solution"]

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.fields['color'].widget = monster_forms.ColorWidget()

    def get_layout(self):
        return Layout(
            Div(
                Field('titel', wrapper_class='col-12 col-sm-9'),
                Field('color', wrapper_class='col-12 col-sm-3'),
            css_class='row align-items-center'),
            "content", "solution",
        )


@crispy(form_tag=False)
class SpielerPageForm(forms.ModelForm):
    class Meta:
        model = SpielerPage
        fields = ["answer"]


@crispy(form_tag=False)
class InquiryForm(forms.ModelForm):
    class Meta:
        model = Inquiry
        fields = ["question", "spieler", "page"]

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.fields['spieler'].widget = HiddenInput()
        self.fields['page'].widget = HiddenInput()
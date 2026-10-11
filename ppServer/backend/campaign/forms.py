import json

from django import forms

from crispy_forms.layout import Layout, Div, Field
from base.crispy_form_decorator import crispy


@crispy(form_tag=False)
class AuswertungForm(forms.Form):

    story = forms.CharField(label="Story", required=False)

    ep = forms.IntegerField(initial=0, label="EP", required=True)
    sp = forms.IntegerField(initial=0, label="SP", required=True)
    geld = forms.IntegerField(initial=0, label="Geld", required=True)
    prestige = forms.IntegerField(initial=0, label="Prestige", required=True)
    verzehr = forms.IntegerField(initial=0, label="Verzehr", required=True)

    def get_layout(self):
        return Layout(
            "story",
            Div(
                Field('ep', wrapper_class='col-12 col-sm'),
                Field('sp', wrapper_class='col-12 col-sm'),
                Field('geld', wrapper_class='col-12 col-sm'),
            css_class='row'),
            Div(
                Field('prestige', wrapper_class='col-12 col-sm'),
                Field('verzehr', wrapper_class='col-12 col-sm'),
            css_class='row'),
        )


class ZauberplätzeWidget(forms.MultiWidget):

    def __init__(self, *args, **kwargs):

        self.template_name="campaign/zauberplätze_widget.html"
        widgets = [forms.NumberInput, forms.NumberInput]

        super().__init__(widgets, *args, **kwargs)

    def get_context(self, name, value, attrs):
        res = super().get_context(name, value, attrs)
        res["widget"]["subwidgets"][0]["attrs"].update({"class": "form-control", "min": 1, "max": 60, "aria-label": "Stufe"})
        res["widget"]["subwidgets"][1]["attrs"].update({"class": "form-control", "min": 1, "aria-label": "Anzahl"})
        return res

    def decompress(self, value):
        if not value or not json.loads(value): return [None, None]
        for stufe, anz in json.loads(value).items():
            return [int(stufe), anz]


    def value_from_datadict(self, data, files, name):
        widget_values = super().value_from_datadict(data, files, name)
        stufe = widget_values[0]
        anzahl = int(widget_values[1] or '0')

        if anzahl and stufe:
            return {stufe: anzahl}
        return {}


@crispy(form_tag=False)
class LarpAuswertungForm(forms.Form):

    story = forms.CharField(label="Story", required=False)

    ap = forms.IntegerField(initial=0, label="AP", required=True)
    fp = forms.IntegerField(initial=0, label="FP", required=True)
    fg = forms.IntegerField(initial=0, label="FG", required=True)
    zauberplätze = forms.JSONField(label="Zauberplätze", required=False, widget=ZauberplätzeWidget(attrs={'class': 'zauberplätze-input'}))
    sp = forms.IntegerField(initial=0, label="SP", required=True)
    geld = forms.IntegerField(initial=0, label="Geld", required=True)
    larp_rang = forms.IntegerField(initial=0, label="LARP-Ränge", required=True)
    prestige = forms.IntegerField(initial=0, label="Prestige", required=True)
    verzehr = forms.IntegerField(initial=0, label="Verzehr", required=True)

    def get_layout(self):
        return Layout(
            "story",
            Div(
                Field('ap', wrapper_class='col-sm'),
                Field('fp', wrapper_class='col-sm'),
                Field('fg', wrapper_class='col-sm'),
            css_class='row'),
            Div(
                Field('sp', wrapper_class='col-sm'),
                Field('geld', wrapper_class='col-sm'),
            css_class='row'),
            Div(
                Field('larp_rang', wrapper_class='col-sm'),
            css_class='row'),
            Div(
                Field('prestige', wrapper_class='col-sm'),
                Field('verzehr', wrapper_class='col-sm'),
            css_class='row'),
            "zauberplätze",
        )
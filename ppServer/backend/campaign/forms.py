import json

from django import forms

from crispy_forms.layout import Layout, Div, Field
from base.crispy_form_decorator import crispy


@crispy(form_tag=False)
class AuswertungForm(forms.Form):

    story = forms.CharField(label="Story", required=False)

    ep = forms.IntegerField(initial=0, min_value=0, label="EP", required=True)
    sp = forms.IntegerField(initial=0, min_value=0, label="SP", required=True)
    geld = forms.IntegerField(initial=0, min_value=0, label="Geld", required=True)
    prestige = forms.IntegerField(initial=0, min_value=0, label="Prestige", required=True)
    verzehr = forms.IntegerField(initial=0, min_value=0, label="Verzehr", required=True)

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

@crispy(form_tag=False)
class LarpAuswertungForm(forms.Form):

    story = forms.CharField(label="Story", required=False)

    ap = forms.IntegerField(initial=0, min_value=0, label="AP", required=True)
    fp = forms.IntegerField(initial=0, min_value=0, label="FP", required=True)
    fg = forms.IntegerField(initial=0, min_value=0, label="FG", required=True)
    zauber_upgrade_points = forms.IntegerField(initial=0, min_value=0, label="Upgradepoints für alle Zauber", required=True)
    sp = forms.IntegerField(initial=0, min_value=0, label="SP", required=True)
    geld = forms.IntegerField(initial=0, min_value=0, label="Geld", required=True)
    larp_rang = forms.IntegerField(initial=0, min_value=0, label="LARP-Ränge", required=True)
    prestige = forms.IntegerField(initial=0, min_value=0, label="Prestige", required=True)
    verzehr = forms.IntegerField(initial=0, min_value=0, label="Verzehr", required=True)

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
                Field('zauber_upgrade_points', wrapper_class='col-sm'),
            css_class='row'),
            Div(
                Field('prestige', wrapper_class='col-sm'),
                Field('verzehr', wrapper_class='col-sm'),
            css_class='row'),
        )
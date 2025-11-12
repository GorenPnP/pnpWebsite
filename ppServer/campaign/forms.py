from django import forms

from crispy_forms.layout import Layout, Div, Field
from base.crispy_form_decorator import crispy


@crispy(form_tag=False)
class AuswertungForm(forms.Form):

    story = forms.CharField(label="Story", required=True)

    ep = forms.IntegerField(initial=0, label="EP", required=True, min_value=1)
    sp = forms.IntegerField(initial=0, label="SP", required=True)
    geld = forms.IntegerField(initial=0, label="Geld", required=True)
    rang = forms.IntegerField(initial=0, label="Ränge", required=True)
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
                Field('rang', wrapper_class='col-12 col-sm'),
                Field('prestige', wrapper_class='col-12 col-sm'),
                Field('verzehr', wrapper_class='col-12 col-sm'),
            css_class='row'),
        )


class ZauberplätzeWidget(forms.MultiWidget):

    def __init__(self, min_stufe=0, max_stufe=30, *args, **kwargs):
        self.MIN_STUFE = min_stufe
        self.MAX_STUFE = max_stufe

        self.template_name="campaign/zauberplätze_widget.html"
        widgets = [forms.NumberInput for stufe in range(self.MIN_STUFE, self.MAX_STUFE+1)]

        super().__init__(widgets, *args, **kwargs)


    def decompress(self, value):
        return [None for _ in range(self.MIN_STUFE, self.MAX_STUFE+1)]


    def value_from_datadict(self, data, files, name):
        amounts_of_stufen = super().value_from_datadict(data, files, name)
        
        result = {}
        for stufe, amount in enumerate(amounts_of_stufen):
            if amount and int(amount) > 0:
                result[str(stufe)] = int(amount)

        return result

    def render(self, name, value, attrs={}, renderer=None):
        attrs["class"] = getattr(attrs, "class", "") + " form-control" # bootstrapy
        return super().render(name, value, attrs, renderer)


@crispy(form_tag=False)
class LarpAuswertungForm(forms.Form):

    story = forms.CharField(label="Story", required=True)

    ap = forms.IntegerField(initial=0, label="AP", required=True)
    fp = forms.IntegerField(initial=0, label="FP", required=True)
    fg = forms.IntegerField(initial=0, label="FG", required=True)
    zauberplätze = forms.JSONField(initial=dict, label="Zauberslots", required=False, widget=ZauberplätzeWidget(attrs={'class': 'zauberplätze-input'}))
    sp = forms.IntegerField(initial=0, label="SP", required=True)
    geld = forms.IntegerField(initial=0, label="Geld", required=True)
    rang = forms.IntegerField(initial=0, label="Ränge", required=True)
    larp_rang = forms.IntegerField(initial=0, label="LARP-Ränge", required=True)
    prestige = forms.IntegerField(initial=0, label="Prestige", required=True)
    verzehr = forms.IntegerField(initial=0, label="Verzehr", required=True)

    def get_layout(self):
        return Layout(
            "story",
            Div(
                Field('ap', wrapper_class='col-12 col-sm'),
                Field('fp', wrapper_class='col-12 col-sm'),
                Field('fg', wrapper_class='col-12 col-sm'),
            css_class='row'),
            Div(
                Field('sp', wrapper_class='col-12 col-sm'),
                Field('geld', wrapper_class='col-12 col-sm'),
            css_class='row'),
            "zauberplätze",
            Div(
                Field('rang', wrapper_class='col-12 col-sm'),
                Field('larp_rang', wrapper_class='col-12 col-sm'),
            css_class='row'),
            Div(
                Field('prestige', wrapper_class='col-12 col-sm'),
                Field('verzehr', wrapper_class='col-12 col-sm'),
            css_class='row'),
        )
from django import forms

class AuswertungForm(forms.Form):

    story = forms.CharField(label="Story", required=True)

    ep = forms.IntegerField(initial=0, label="EP", required=True, min_value=1)
    sp = forms.IntegerField(initial=0, label="SP", required=True)
    rang = forms.IntegerField(initial=0, label="Ränge", required=True)
    prestige = forms.IntegerField(initial=0, label="Prestige", required=True)
    verzehr = forms.IntegerField(initial=0, label="Verzehr", required=True)


class ZauberplätzeWidget(forms.MultiWidget):

    def __init__(self, min_stufe=0, max_stufe=30, *args, **kwargs):
        self.MIN_STUFE = min_stufe
        self.MAX_STUFE = max_stufe

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

class LarpAuswertungForm(forms.Form):

    story = forms.CharField(label="Story", required=True)

    ap = forms.IntegerField(initial=0, label="AP", required=True)
    fp = forms.IntegerField(initial=0, label="FP", required=True)
    fg = forms.IntegerField(initial=0, label="FG", required=True)
    zauberplätze = forms.JSONField(initial=dict, label="Zauberslots", required=False, widget=ZauberplätzeWidget(attrs={'class': 'zauberplätze-input'}))
    sp = forms.IntegerField(initial=0, label="SP", required=True)
    rang = forms.IntegerField(initial=0, label="Ränge", required=True)
    prestige = forms.IntegerField(initial=0, label="Prestige", required=True)
    verzehr = forms.IntegerField(initial=0, label="Verzehr", required=True)

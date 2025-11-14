from django import forms

from base.crispy_form_decorator import crispy

from .models import Proposal

@crispy(form_tag=False)
class ProposalForm(forms.ModelForm):
    class Meta:
        model = Proposal
        fields = ["start", "note"]

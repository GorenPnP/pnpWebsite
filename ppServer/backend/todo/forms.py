from django import forms

from .models import *

class CreateIntervalForm(forms.ModelForm):
    class Meta:
        model = TimeInterval
        fields = ["category", "start", "end"]


class CreateCategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ["name", "color", "textColor"]
from django import forms
from django.forms import ValidationError, modelformset_factory

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div, Field

from .models import Region, CellType, RegionEnemy

class RegionEditorForm(forms.ModelForm):
    class Meta:
        model = Region
        fields = ["grid", "enemies"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["grid"].widget = forms.HiddenInput()

    def clean_grid(self):

        if "grid" not in self.cleaned_data or len(self.cleaned_data["grid"]) != Region.GRID_SIZE **2:
            raise ValidationError("Grid ist nicht da/hat die falsche Größe")

        grid = self.cleaned_data["grid"]

        if not CellType.objects.filter(exit=True, pk__in=grid).exists():
            raise ValidationError(f"Grid enthält keinen Ausgang")
        if not CellType.objects.filter(spawn=True, pk__in=grid).exists():
            raise ValidationError(f"Grid enthält keinen Spawn")
        if not CellType.objects.filter(enemy_spawn=True, pk__in=grid).exists():
            raise ValidationError(f"Grid enthält keinen Gegner")

        cell_types = list(CellType.objects.values_list("pk", flat=True))
        for cell in set(grid):
            if cell not in cell_types:
                raise ValidationError(f"Grid enthält nicht-konforme Zelle {cell}")

        return self.cleaned_data["grid"]


def get_EnemyFormset(region: Region):
    return modelformset_factory(RegionEnemy, fields = ["enemy", "num"], extra=RegionEnemy.objects.filter(region=region).count()+3, can_delete=True)

class EnemyFormsetHelper(FormHelper):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.form_tag = False
        self.layout = Layout(
            Div(
                Field('enemy'),
                Field('num'),
                Field('DELETE'),
            css_class='enemy-row'),
        )
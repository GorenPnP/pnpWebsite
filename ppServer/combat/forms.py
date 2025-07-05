from django import forms
from django.forms import ValidationError


from .models import Region, CellType

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

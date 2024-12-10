from django import forms
from django.db.models import Model


def PopulatedFormSet(parent_model: Model, db_model: Model, prefix: str, fieldname_of_fk: str, display_fields: list[str]) -> forms.BaseInlineFormSet:
    # get initial & count for initializing later
    populateable_field = db_model._meta.get_field(fieldname_of_fk)
    try:
        FkModel = populateable_field.remote_field.model

        queryset = FkModel.objects.all().select_related()
        choices = None
        initial = [{fieldname_of_fk: obj} for obj in queryset]
        count = FkModel.objects.count()
    except:
        queryset = None
        choices = populateable_field.choices
        initial = [{fieldname_of_fk: obj} for obj, _ in choices]
        count = len(choices)

    # classes
    class _Form(forms.ModelForm):
        class Meta:
            model = db_model
            fields = display_fields

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.fields[fieldname_of_fk].disabled = True
            if queryset: self.fields[fieldname_of_fk].queryset = queryset
            if choices: self.fields[fieldname_of_fk].choices = choices

    class _FormSet(forms.BaseInlineFormSet):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **{
                **kwargs,
                "initial": getattr(kwargs, "initial", initial),
                "prefix": getattr(kwargs, "prefix", prefix),
                "queryset": db_model.objects.select_related("char"),
            })

    # use formset factory
    return forms.inlineformset_factory(parent_model=parent_model, model=db_model, form=_Form, formset=_FormSet, min_num=count, max_num=count, absolute_max=count,
        extra=0, can_order=False, can_delete=False, validate_min=False, validate_max=True
    )




def FormSet(parent_model: Model, db_model: Model, prefix: str, display_fields: list[str]) -> forms.BaseInlineFormSet:
    class _FormSet(forms.BaseInlineFormSet):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **{
                **kwargs,
                "prefix": getattr(kwargs, "prefix", prefix),
                "queryset": db_model.objects.select_related("char"),
            })

    # use formset factory
    return forms.inlineformset_factory(parent_model=parent_model, model=db_model, fields=display_fields, formset=_FormSet,
        can_order=False, validate_min=False, validate_max=True, extra=1, can_delete=True
    )

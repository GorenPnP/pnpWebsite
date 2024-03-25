from functools import reduce
from operator import or_

from django.contrib import admin
from django.db import models
from django.db.models import fields, Subquery, Window, Avg, Q

def get_filter(model: models.Model, model_field: str, fields: list[str]):
    """
    returns a admin.SimpleFilter
    example usage (on FertigkeitAdmin):
        get_filter(Attribut, "titel", ["attr__titel"])

    model: Model is the model the filter displays, e.g. Attribut if you want to filter Fertigkeiten by Attribut
    model_field: str is the name of the model's field to display & use as filter. can be "titel" to filter the Attribute by titel
    fields: str[] are names on the admin's model to filter the queryset (of Fertigkeiten) by. they should match model->model_field (e.g. Fertigkeit.attr__titel matches Attribut.titel). Fields are || connected
    """
    
    class Filter(admin.SimpleListFilter):
        # Human-readable title which will be displayed in the
        # right admin sidebar just above the filter options.
        title = model._meta.verbose_name

        # Parameter for the filter that will be used in the URL query.
        parameter_name = model._meta.model_name + "__" + model_field

        def lookups(self, request, model_admin):
            """
            Returns a list of tuples. The first element in each
            tuple is the coded value for the option that will
            appear in the URL query. The second element is the
            human-readable name for the option that will appear
            in the right sidebar.
            """
            qs = model_admin.get_queryset(request)
            vals = set()
            for field in fields: vals.update(qs.values_list(field, flat=True))

            filter = {model_field + "__in": vals}
            return [(field, field) for field in model.objects.filter(**filter).values_list(model_field, flat=True)]

        def queryset(self, request, queryset):
            """
            Returns the filtered queryset based on the value
            provided in the query string and retrievable via
            `self.value()`.
            """
            value = self.value()
            if not value or not fields or not len(fields): return queryset

            if len(fields) == 1: return queryset.filter(**{fields[0]: value})

            filter_rules = [Q(**{field:value}) for field in fields]
            return queryset.filter(reduce(or_, filter_rules))
    return Filter


class ConcatSubquery(Subquery):
    """ Concat queryset that stems from a subquery to a string.
        queryset objects may only have ONE FIELD (-> use .values('name') at the end for example):
    >>> qs = Product.objects.all().values('name')
    >>> Store.objects.all().annotate(
            products=ConcatSubquery(qs)
        )
    <StoreQuerySet [
        {..., 'products': ''},
        {..., , 'products': 'Playera con abertura ojal'},
        {..., 'products': 'Diabecreme, Diabecreme, Diabecreme, Caída Cabello, Intensif, Smooth, Repairing'}
        ...
    ]>

    ConcatSubquery can take an optional separator (default is ", "): ConcatSubquery(qs, separator=" + ")

    Base version: https://leonardoramirezmx.medium.com/how-to-concat-subquery-on-django-orm-cce32371a693
    """
    template = 'ARRAY_TO_STRING(ARRAY(%(subquery)s), %(separator)s)'

    def __init__(self, queryset, separator=', ', **kwargs):
        self.separator = separator
        super().__init__(queryset, fields.CharField(), **kwargs)

    def as_sql(self, compiler, connection, template=None, **extra_context):
        extra_context['separator'] = '%s'
        sql, sql_params = super().as_sql(compiler, connection, template, **extra_context)
        return sql, sql_params + (self.separator, )


class AvgSubquery(Subquery):

    def __init__(self, queryset, field, **kwargs):
        queryset = queryset.annotate(
            total=Window(
                expression=Avg(field),
            )
        ).values('total')[:1]

        super().__init__(queryset, fields.IntegerField(), **kwargs)


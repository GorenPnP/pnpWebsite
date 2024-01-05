from django.db.models import fields, Subquery, Window, Avg


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


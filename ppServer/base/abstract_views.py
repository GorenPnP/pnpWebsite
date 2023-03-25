import math

from django.core.exceptions import ImproperlyConfigured
from django.urls import reverse

from django_filters.views import FilterView

import django_tables2 as tables
from django_tables2.export.views import ExportMixin
from django_tables2.views import SingleTableMixin


class GenericTable(tables.Table):
    class Meta:
        attrs = {"class": "table table-dark table-striped table-hover"}

class DynamicTableView(ExportMixin, SingleTableMixin, FilterView):

    #### GENERAL ####

    # model = <an optional model. You will need a queryset if not set>
    # queryset = <some optional queryset. default will be self.model.objects.all()>

    # topic/title of page & file export
    topic = None
    plus_url = None

    # template
    template_name = "base/dynamic-table.html"


    #### OPTIONAL TABLE & FILTER SPECS ####

    # an optional django_filters.FilterSet instance to filter the table content
    filterset_class = None
    # OR a list or dict containing the fields of self.model to filter for
    filterset_fields = None

    # an optional django_tables2.tables.Table instance to control the table appearance
    table_class = None
    

    #### EXPORT ####

    # exported file name. Default is self.topic
    export_name = None
    # options are: ["csv", "json", "latex", "ods", "tsv", "xls", "xlsx", "yaml"]
    export_formats = []


    def get_export_filename(self, export_format):
        return f"{self.export_name or self.topic}.{export_format}"

    def get_dataset_kwargs(self):
        return {"title": self.topic}.update(self.dataset_kwargs or {})
    
    def get_topic(self):
        return self.topic or self.model._meta.verbose_name_plural or None

    def get_plus_url(self):
        return reverse(self.plus_url) if self.plus_url else None

    def get_table_class(self):
        """
        Return the class to use for the table.
        """
        if self.table_class:
            return self.table_class
        if self.model:
            return tables.table_factory(self.model, table=GenericTable, fields=self.table_fields)

        name = type(self).__name__
        raise ImproperlyConfigured(f"You must either specify {name}.table_class or {name}.model")

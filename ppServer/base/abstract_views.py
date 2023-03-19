from django.urls import reverse

from django_filters.views import FilterView

from django_tables2.export.views import ExportMixin
from django_tables2.views import SingleTableMixin


class DynamicTableView(ExportMixin, SingleTableMixin, FilterView):

    #### GENERAL ####

    # model = <an optional model. You will need a queryset if not set>
    # queryset = <some optional queryset. default will be self.model.objects.all()>

    # topic/title of page & file export
    topic = "some table"
    plus_url = None

    # template
    template_name = "base/dynamic-table.html"


    #### OPTIONAL TABLE & FILTER SPECS ####

    # an optional django_filters.FilterSet instance to filter the table content
    filterset_class = None

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
        return self.topic or None

    def get_plus_url(self):
        return reverse(self.plus_url) if self.plus_url else None

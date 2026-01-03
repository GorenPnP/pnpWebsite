import math

from django.core.exceptions import ImproperlyConfigured
from django.urls import reverse

from django_filters.views import FilterView

from django_tables2 import Table, MultiTableMixin, SingleTableMixin, table_factory
from django_tables2.export.views import ExportMixin
from django_tables2.views import SingleTableMixin


class TableView(FilterView):
    #### GENERAL ####

    # model = <an optional model. You will need a queryset if not set>
    # queryset = <some optional queryset. default will be self.model.objects.all()>

    # topic/title of page and other stuff for the header & file export
    topic = None
    plus = None
    plus_url = None
    app_index = None
    app_index_url = None

    def get_dataset_kwargs(self):
        return {"title": self.topic}.update(self.dataset_kwargs or {})

    def get_topic(self):
        return self.topic or self.model._meta.verbose_name_plural or None

    def get_plus(self):
        return self.plus or None
    
    def get_plus_url(self):
        return reverse(self.plus_url) if self.plus_url else None
    
    def get_app_index(self):
        if self.app_index: return self.app_index
        return self.model._meta.app_label.title() if self.model else None

    def get_app_index_url(self):
        if self.app_index_url: return reverse(self.app_index_url)
        return reverse(f"{self.model._meta.app_label}:index") if self.model else None
    
    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)

        # don't clash with other Mixins & stuff
        if "topic" not in context: context["topic"] = self.get_topic()
        if "plus" not in context: context["plus"] = self.get_plus()
        if "plus_url" not in context: context["plus_url"] = self.get_plus_url()
        if "app_index" not in context: context["app_index"] = self.get_app_index()
        if "app_index_url" not in context: context["app_index_url"] = self.get_app_index_url()
        return context


class ExportTableMixin(ExportMixin):
    #### EXPORT ####

    # exported file name. Default is self.topic
    export_name = None
    # don't export following columns
    exclude_columns = []
    # options are: ["csv", "json", "latex", "tsv"]
    export_formats = []

    def get_export_filename(self, export_format):
        return f"{self.export_name or self.topic}.{export_format}"



class GenericTable(Table):
    class Meta:
        attrs = {
            "class": "table table-dark table-striped table-hover",
            "th": {"class": "sticky-top"},
        }

class DynamicTableView(ExportTableMixin, SingleTableMixin, TableView):

    #### GENERAL ####
    # see TableView

    # template
    template_name = "base/dynamic-table.html"


    #### OPTIONAL TABLE & FILTER SPECS ####

    # an optional django_filters.FilterSet instance to filter the table content
    filterset_class = None
    # OR a list or dict containing the fields of self.model to filter for
    filterset_fields = []

    # an optional django_tables2.Table instance to control the table appearance
    table_class = None
    

    #### EXPORT ####
    # see ExportTableMixin


    def get_table_class(self):
        """
        Return the class to use for the table.
        """
        if self.table_class:
            return self.table_class
        if self.model:
            return table_factory(self.model, table=GenericTable, fields=self.table_fields)

        name = type(self).__name__
        raise ImproperlyConfigured(f"You must either specify {name}.table_class or {name}.model")


class DynamicTablesView(MultiTableMixin, TableView):
    #### GENERAL ####
    # see TableView

    # template
    template_name = "base/dynamic-tables.html"


    #### MULTIPLE TABLES ####

    # list[Table]: Tables might be all instantiated or not. If not, tables_data has to be set or get_tables_data() has to return suitable values
    tables = []

    # arguments to Table.__init__() call of those in self.tables (in same order)
    tables_data = []

    table_prefix = "table_{}-"

    ## FROM MultiTableMixin: ##
    # def get_tables_data(self):
    #     """
    #     Return an array of table_data that should be used to populate each table
    #     """
    #     return self.tables_data


    #### OPTIONAL TABLE & FILTER SPECS (would filter over ALL Tables?) ####

    # an optional django_filters.FilterSet instance to filter the table content
    filterset_class = None
    # OR a list or dict containing the fields of self.model to filter for
    filterset_fields = []

    # an optional django_tables2.Table instance to control the table appearance
    table_class = None
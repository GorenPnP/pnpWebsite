from typing import Any, Dict

from django.apps import apps
from django.core.exceptions import ImproperlyConfigured
from django.db.models import Max, Min, Value
from django.db.models.query import QuerySet
from django.shortcuts import reverse
from django.utils.html import format_html
from django.views.generic import TemplateView

from django_filters import FilterSet, NumberFilter
import django_tables2 as tables
from django_tables2.export.views import ExportMixin
from django_tables2.views import SingleTableMixin

from base.abstract_views import DynamicTableView, GenericTable
from log.create_log import render_number
from ppServer.mixins import VerifiedAccountMixin

from ..models import *


########################################################################
######################### all at once ##################################
########################################################################

model_list = [
    Item,
    Waffen_Werkzeuge,
    Magazin,
    Pfeil_Bolzen,
    Schusswaffen,
    Magische_Ausrüstung,
    Rituale_Runen,
    Rüstungen,
    Ausrüstung_Technik,
    Fahrzeug,
    Einbauten,
    Zauber,
    VergessenerZauber,
    Alchemie,
    Tinker,
    Begleiter,
    Engelsroboter,
]
    

class FullShopTableView(VerifiedAccountMixin, ExportMixin, SingleTableMixin, TemplateView):

    class Table(GenericTable):
        class Meta:
            attrs = GenericTable.Meta.attrs

        icon = tables.Column(orderable=False)
        name = tables.Column()
        beschreibung = tables.Column()
        ab_stufe = tables.Column()
        preis = tables.Column()
        art = tables.Column()

        def render_icon(self, value, record):
            # use python model .objects.get().getIconUrl()
            Model = apps.get_model('shop', record["model_name"])
            instance = Model.objects.get(id=record["id"])

            return format_html("<img src='{url}'>", url=instance.getIconUrl())

        def render_name(self, value, record):
            try:
                url = reverse("shop:buy_{}".format(record["model_name"]), args=[record["id"]])
                return format_html("<a href='{url}'>{name}</a>", url=url, name=value)
            except:
                return value
        def value_name(self, value):
            return value

        def render_beschreibung(self, value):
            return format_html(value.replace("\n", "<br>"))
        def value_beschreibung(self, value):
            return value

        def render_preis(self, value, record):
            preis = "{}{}".format(render_number(value), " - {}".format(render_number(record["max_preis"])) if record["max_preis"] != value else "")

            if record["stufenabhängig"]: return f"{preis} Dr * Stufe"
            if record["model_name"] == "rituale_runen": return f"Stufe 1: {preis} Dr."

            return f"{preis} Dr."

    table_class = Table

    template_name = "shop/show_all.html"

    export_name = "kompletter shop"
    exclude_columns = ["icon"]
    export_formats = ["csv", "json", "latex", "tsv"]

    def get_topic(self): return "Shop"
    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        return super().get_context_data(**kwargs, topic=self.get_topic())

    def get_table_data(self):
        """
        Return the table data that should be used to populate the rows.
        """
        if self.table_data is not None:
            return self.table_data
        

        # construct filters from query params. use only ones with "__". ignoring page, ordering, etc.
        filters = {}
        for key, values in self.request.GET.items():
            if "__" not in key or not values or not len(values): continue

            # number_fields are "ab_stufe", "preis"
            filters[key] = int(values) if key.startswith("ab_stufe") or key.startswith("preis") else values
        

        # get filtered objects
        objects = []
        for Model in model_list:
            model_name = Model._meta.model_name

            # construct base queryset without frei_editierbare instances
            model_verbose = Model._meta.verbose_name
            queryset = Model.objects\
                .filter(frei_editierbar=False)\
                .annotate(
                    model_name=Value(model_name),
                    art=Value(model_verbose)
                )
            
            # annotate non-tinker instances with their prices
            if model_name != "tinker":
                field = "preis" if model_name != "rituale_runen" else "stufe_1"

                queryset = queryset\
                    .prefetch_related("firmen")\
                    .annotate(
                        preis=Min('firma{}__{}'.format(Model._meta.model_name, field)),
                        max_preis=Max('firma{}__{}'.format(Model._meta.model_name, field))
                    )

            # tinker-instances don't have a price. remove price from filter
            if model_name == "tinker" and "preis__lte" in filters:
                filters = {**filters}
                del filters["preis__lte"]
            
            # filter queryset and return as dict
            objects += queryset\
                .filter(**filters)\
                .values()

        # return objects (ordered by name)
        return sorted(objects, key=lambda a: a["name"])
    



########################################################################
######################## by Category ###################################
########################################################################


####################### abstract base ##################################

class ShopTable(GenericTable):
    class Meta:
        model = Item
        fields = ("icon", "name", "beschreibung", "ab_stufe", "preis")
        order_by_field = "name"

        attrs = GenericTable.Meta.attrs

    def render_icon(self, value):
        return format_html("<img src='{url}'>", url=value.instance.getIconUrl())

    def render_name(self, value, record):
        return format_html("<a href='{url}'>{name}</a>", url=reverse("shop:buy_{}".format(self._meta.model._meta.model_name), args=[record.pk]), name=value)
    def value_name(self, value):
        return value

    def render_beschreibung(self, value):
        return format_html(value.replace("\n", "<br>"))
    def value_beschreibung(self, value):
        return value

    def render_preis(self, value, record):
        preis = "{}{}".format(render_number(value), " - {}".format(render_number(record.max_preis)) if record.max_preis != value else "")
        return "{} Dr.{}".format(preis, " * Stufe" if record.stufenabhängig else "")

    # TODO add:
    # illegal = models.BooleanField(default=False)
    # lizenz_benötigt = models.BooleanField(default=False)


class ShopFilter(FilterSet):
    class Meta:
        model = Item
        fields = {
            "name": ["icontains"],
            "beschreibung": ["icontains"],
            "ab_stufe": ["lte"],
        }

    preis = NumberFilter(
        field_name="preis",
        method="filter_preis",
        label="Preis ist kleiner oder gleich",
    )

    def filter_preis(self, queryset, name, value):
        return queryset.prefetch_related("firmen").annotate(
            preis=Min('firma{}__preis'.format(self._meta.model._meta.model_name)),
        ).filter(preis__lte=value)


class ShopTableView(VerifiedAccountMixin, DynamicTableView):

    model = None
    filterset_class = None
    table_class = None

    export_name = "<shop>"
    exclude_columns = ["icon"]
    export_formats = ["csv", "json", "latex", "tsv"]

    def get_export_filename(self, export_format):
        return super().get_export_filename(export_format).replace("<shop>", self.model._meta.verbose_name_plural)

    def get_queryset(self) -> QuerySet[Any]:
        return super().get_queryset().filter(frei_editierbar=False).prefetch_related("firmen").annotate(
            max_preis=Max('firma{}__preis'.format(self.model._meta.model_name)),
            preis=Min('firma{}__preis'.format(self.model._meta.model_name)),
        ).order_by("name")

    def get_topic(self):
        if self.model:
            return self.model._meta.verbose_name_plural or super().get_topic()
        return super().get_topic()

    def get_plus(self):
        if not self.model: return super().get_plus()
        return f"+ {self.model._meta.verbose_name}"

    def get_plus_url(self):
        if not self.model: return super().get_plus_url()
        return reverse("admin:{}_{}_add".format(self.model._meta.app_label, self.model._meta.model_name))

    def get_table_class(self):
        """
        Return the class to use for the table.
        """
        if self.table_class:
            return self.table_class
        if self.model:
            return tables.table_factory(self.model, table=ShopTable, fields=self.table_fields)

        name = type(self).__name__
        raise ImproperlyConfigured(f"You must either specify {name}.table_class or {name}.model")






############################### views ########################################

class ItemTableView(ShopTableView):
    model = Item
    filterset_fields = ShopFilter._meta.fields
    table_fields = ("icon", "name", "beschreibung", "ab_stufe", "preis")


class WaffenWerkzeugeTableView(ShopTableView):
    model = Waffen_Werkzeuge
    filterset_fields = {**ShopFilter._meta.fields,
        "erfolge": ["icontains"],
        "bs": ["icontains"],
        "zs": ["icontains"],
        "dk": ["lte"],
        "schadensart": ["exact"]
    }
    table_fields = ("icon", "name", "beschreibung", "ab_stufe", "erfolge", "bs", "zs", "dk", "schadensart", "preis")


class MagazinTableView(ShopTableView):
    model = Magazin
    filterset_fields = {**ShopFilter._meta.fields, "schuss": ["exact"]}
    table_fields = ("icon", "name", "beschreibung", "ab_stufe", "schuss", "preis")


class PfeilBolzenTableView(ShopTableView):
    model = Pfeil_Bolzen
    filterset_fields = {**ShopFilter._meta.fields, "bs": ["icontains"], "zs": ["icontains"], "schadensart": ["exact"]}
    table_fields = ("icon", "name", "beschreibung", "ab_stufe", "bs", "zs", "schadensart", "preis")


class SchusswaffenTableView(ShopTableView):
    model = Schusswaffen
    filterset_fields = {**ShopFilter._meta.fields,
                "erfolge": ["exact"],
                "bs": ["icontains"],
                "zs": ["icontains"],
                "dk": ["exact"],
                "präzision": ["exact"],
                "schadensart": "exact"
            }
    table_fields = ("icon", "name", "beschreibung", "ab_stufe", "erfolge", "bs", "zs", "dk", "präzision", "schadensart", "preis")


class MagischeAusrüstungTableView(ShopTableView):
    model = Magische_Ausrüstung
    filterset_fields = ShopFilter._meta.fields
    table_fields = ("icon", "name", "beschreibung", "ab_stufe", "preis")


class RitualeRunenTableView(ShopTableView):
    class Filter(FilterSet):
        class Meta:
            model = Rituale_Runen
            fields = {
                "name": ["icontains"],
                "beschreibung": ["icontains"],
                "ab_stufe": ["lte"],
            }

        stufe_1 = NumberFilter(
            field_name="stufe_1",
            method="filter_stufe",
            label="Preis für Stufe 1 ist kleiner oder gleich",
        )
        stufe_2 = NumberFilter(
            field_name="stufe_2",
            method="filter_stufe",
            label="Preis für Stufe 2 ist kleiner oder gleich",
        )
        stufe_3 = NumberFilter(
            field_name="stufe_3",
            method="filter_stufe",
            label="Preis für Stufe 3 ist kleiner oder gleich",
        )
        stufe_4 = NumberFilter(
            field_name="stufe_4",
            method="filter_stufe",
            label="Preis für Stufe 4 ist kleiner oder gleich",
        )
        stufe_5 = NumberFilter(
            field_name="stufe_5",
            method="filter_stufe",
            label="Preis für Stufe 5 ist kleiner oder gleich",
        )
    
        def filter_stufe(self, queryset, name, value):
            return queryset.prefetch_related("firmen").annotate(
                stufe=Min('firma{}__{}'.format(self._meta.model._meta.model_name, name)),
            ).filter(stufe__lte=value)

    class Table(ShopTable):
        class Meta:
            model = Rituale_Runen
            fields = ("icon", "name", "beschreibung", "ab_stufe", "stufe_1", "stufe_2", "stufe_3", "stufe_4", "stufe_5")
            attrs = GenericTable.Meta.attrs

        def _render_stufe_x(self, value, record, column):
            max_value = getattr(record, column.accessor + "_max")
            return "{}{} Dr.".format(value, " - "+str(max_value) if value != max_value else "")

        def render_stufe_1(self, value, record, column):
            return self._render_stufe_x(value, record, column)
        def render_stufe_2(self, value, record, column):
            return self._render_stufe_x(value, record, column)
        def render_stufe_3(self, value, record, column):
            return self._render_stufe_x(value, record, column)
        def render_stufe_4(self, value, record, column):
            return self._render_stufe_x(value, record, column)
        def render_stufe_5(self, value, record, column):
            return self._render_stufe_x(value, record, column)

    model = Rituale_Runen
    filterset_class = Filter
    table_class = Table


    def get_queryset(self) -> QuerySet[Any]:
        return self.model.objects.filter(frei_editierbar=False).order_by("name")\
        .prefetch_related("firmen").annotate(
            stufe_1=Min('firma{}__stufe_1'.format(self.model._meta.model_name)),
            stufe_1_max=Max('firma{}__stufe_1'.format(self.model._meta.model_name)),
            stufe_2=Min('firma{}__stufe_2'.format(self.model._meta.model_name)),
            stufe_2_max=Max('firma{}__stufe_2'.format(self.model._meta.model_name)),
            stufe_3=Min('firma{}__stufe_3'.format(self.model._meta.model_name)),
            stufe_3_max=Max('firma{}__stufe_3'.format(self.model._meta.model_name)),
            stufe_4=Min('firma{}__stufe_4'.format(self.model._meta.model_name)),
            stufe_4_max=Max('firma{}__stufe_4'.format(self.model._meta.model_name)),
            stufe_5=Min('firma{}__stufe_5'.format(self.model._meta.model_name)),
            stufe_5_max=Max('firma{}__stufe_5'.format(self.model._meta.model_name))
        )


class RüstungenTableView(ShopTableView):
    model = Rüstungen
    filterset_fields = {**ShopFilter._meta.fields,
        "schutz": ["gte"],
        "stärke": ["gte"],
        "haltbarkeit": ["gte"]
    }
    table_fields = ("icon", "name", "beschreibung", "ab_stufe", "schutz", "stärke", "haltbarkeit",  "preis")


class AusrüstungTechnikTableView(ShopTableView):
    model = Ausrüstung_Technik
    filterset_fields = ShopFilter._meta.fields
    table_fields = ("icon", "name", "beschreibung", "ab_stufe", "preis")


class FahrzeugTableView(ShopTableView):
    model = Fahrzeug
    filterset_fields = {**ShopFilter._meta.fields,
        "schnelligkeit": ["gte"],
        "rüstung": ["gte"],
        "erfolge": ["lte"],
    }
    table_fields = ("icon", "name", "beschreibung", "ab_stufe", "schnelligkeit", "rüstung", "erfolge", "preis")


class EinbautenTableView(ShopTableView):
    model = Einbauten
    filterset_fields = {**ShopFilter._meta.fields, "manifestverlust": ["icontains"]}
    table_fields = ("icon", "name", "beschreibung", "ab_stufe", "manifestverlust", "preis")


class ZauberTableView(ShopTableView):
    model = Zauber
    filterset_fields = {**ShopFilter._meta.fields,
        "schaden": ["icontains"],
        "astralschaden": ["icontains"],
        "manaverbrauch": ["icontains"],
        "astralsch_is_direct": ["exact"],
        "verteidigung": ["exact"],
        "kategorie": ["exact"],
        "schadensart": ["exact"]
    }
    table_fields = ("icon", "name", "beschreibung", "ab_stufe", "schaden", "astralschaden", "astralsch_is_direct", "manaverbrauch", "verteidigung", "schadensart", "kategorie", "preis")


class VergessenerZauberTableView(ShopTableView):
    model = VergessenerZauber
    filterset_fields = {**ShopFilter._meta.fields,
        "schaden": ["icontains"],
        "astralschaden": ["icontains"],
        "manaverbrauch": ["icontains"]
    }
    table_fields = ("icon", "name", "beschreibung", "ab_stufe", "schaden", "astralschaden", "manaverbrauch", "preis")


class AlchemieTableView(ShopTableView):
    model = Alchemie
    filterset_fields = ShopFilter._meta.fields
    table_fields = ("icon", "name", "beschreibung", "ab_stufe", "preis")


class TinkerTableView(ShopTableView):
    class Table(ShopTable):
        class Meta:
            model = Tinker
            fields = ("icon", "name", "beschreibung", "ab_stufe", "werte", "preis")
            attrs = GenericTable.Meta.attrs

        def render_name(self, value):
            return value

    model = Tinker
    filterset_fields = {**ShopFilter._meta.fields, "werte": ["icontains"]}
    table_class = Table


class BegleiterTableView(ShopTableView):
    model = Begleiter
    filterset_fields = ShopFilter._meta.fields
    table_fields = ("icon", "name", "beschreibung", "ab_stufe", "preis")


class EngelsroboterTableView(ShopTableView):
    model = Engelsroboter
    filterset_fields = {**ShopFilter._meta.fields,
        'ST': ["gte"],
        'UM': ["gte"],
        'MA': ["gte"],
        'IN': ["gte"],
    }
    table_fields = ("icon", "name", "beschreibung", "ab_stufe", 'ST', 'UM', 'MA', 'IN', "preis")

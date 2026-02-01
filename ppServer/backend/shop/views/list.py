import re
from typing import Any, Dict

from django.apps import apps
from django.core.exceptions import ImproperlyConfigured
from django.db.models import Max, Min, Value, TextField, F, ManyToManyField, OuterRef
from django.db.models.fields import BooleanField
from django.db.models.functions import Concat
from django.db.models.query import QuerySet
from django.shortcuts import reverse
from django.utils.html import format_html
from django.views.generic import TemplateView

from django_filters import FilterSet, NumberFilter, CharFilter
import django_tables2 as tables
from django_tables2.export.views import ExportMixin
from django_tables2.views import SingleTableMixin

from base.abstract_views import DynamicTableView, GenericTable
from log.create_log import render_number
from ppServer.mixins import VerifiedAccountMixin
from ppServer.utils import ConcatSubquery, display_value

from ..models import *

shopmodel_list = [m for m in apps.get_app_config("shop").get_models() if not m._meta.abstract and m._meta.model_name not in ["modifier", "shopcategory"] and not  m._meta.model_name.startswith("firma")]


def annotate_price(Model: models.Model) -> dict[str, any]:
    
    if hasattr(Model.firmen.rel.through, "preis"):
        return {
            "preis": Min('firma{}__{}'.format(Model._meta.model_name, "preis")),
            "max_preis": Max('firma{}__{}'.format(Model._meta.model_name, "preis")),
        }
    
    # Rituale/Runen
    stufen: list[int] = sorted([int(k.replace("stufe_", "")) for k in Model.firmen.rel.through.__dict__.keys() if re.match(r"^stufe_\d+$", k)])
    if stufen:
        annotations = {
            "preis": Min(f'firma{Model._meta.model_name}__stufe_{stufen[0]}'),
            "max_preis": Max(f'firma{Model._meta.model_name}__stufe_{stufen[0]}'),
        }
        for i in stufen:
            annotations[f"stufe_{i}"] = Min(f'firma{Model._meta.model_name}__stufe_{i}')
            annotations[f"stufe_{i}_max"] = Max(f'firma{Model._meta.model_name}__stufe_{i}')

        return annotations

    return {}

def annotate_other(Model: models.Model, ignore_fields: list[str]) -> dict[str, any]:
    other_fieldnames = [fieldname for fieldname in Model.getShopDisplayFields() if fieldname not in ignore_fields]

    # get all fields displayed on "other"
    other_fields = [field for field in Model._meta.get_fields() if field.name in other_fieldnames]

    # qs-prep: change display in "other"-cell of table at db level (to make it searchable)
    other_concat_parts = []
    displays_of_fields_in_other = {}
    for field in other_fields:
        queryname = f"{field.name}_display"

        # prepare EACH FIELD used in "other" for concat later
        other_concat_parts.append(Value(f"{field.verbose_name}: " if not other_concat_parts else f",\n {field.verbose_name}: "))
        other_concat_parts.append(queryname)


        choices = getattr(field, "choices", []) or []
        # use verbose text of choice/enum
        if choices:
            displays_of_fields_in_other[queryname] = display_value(choices, field.name)

        # translate boolean field values to german
        elif field.__class__ == BooleanField:
            displays_of_fields_in_other[queryname] = display_value([("True", "Ja"), ("False", "Nein")], field.name)

        # resolves M2M with related_object.name
        elif field.__class__ == ManyToManyField:
            displays_of_fields_in_other[queryname] = ConcatSubquery(field.related_model.objects.filter(**{f"{Model._meta.model_name}__id": OuterRef("id")}).values("name"), separator=", ")

        # base case, no changes
        else:
            displays_of_fields_in_other[queryname] = F(field.name)

    # construct base queryset without frei_editierbare instances
    return {
        **displays_of_fields_in_other,
        "other": Concat(*other_concat_parts, output_field=TextField()),
    } if displays_of_fields_in_other else {"other": Value("")}


class RenderableTable(GenericTable):
    class Meta:
        attrs = GenericTable.Meta.attrs
        order_by_field = "name"

    def _get(self, obj, key: str):
        try:
            return getattr(obj, key, obj[key])
        except:
            return obj.__dict__[key] 

    def render_icon(self, value, record):
        Model = apps.get_model('shop', self._get(record, "model_name"))
        instance = Model.objects.get(id=self._get(record, "id"))

        # use python model .objects.get().getIconUrl()
        return format_html("<img src='{url}' loading='lazy'>", url=instance.getIconUrl())

    def render_name(self, value, record):
        try:
            url = reverse(f'shop:buy', args=[apps.get_model("shop", self._get(record, "model_name")), self._get(record, "id")])
            return format_html(f"<a href='{url}'>{value}</a>")
        except:
            return value

    def render_beschreibung(self, value):
        return format_html(value.replace("\n", "<br>"))

    def render_art(self, value, record):
        return self._get(record, "art_display")
    
    def render_preis(self, value, record):
        preis = "{}{}".format(render_number(value), " - {}".format(render_number(self._get(record, "max_preis"))) if self._get(record, "max_preis") != value else "")
        return "{} Dr.{}".format(preis, " * Stufe" if self._get(record, "stufenabhängig") else "")

    def render_other(self, value):

        # build dict; convert "kategory: some stuff,\ntimes: 3" => {kategory: "some stuff", "times": "3"}
        values = {v.split(": ")[0].strip(): v.split(": ")[1].strip() for v in value.split(',\n')}

        # format cell content
        return format_html("<ul><li>" + '</li><li>'.join(f'<em>{k}</em>: {v}' for k, v in values.items()) + "</li></ul>")

########################################################################
######################### all at once ##################################
########################################################################

class FullShopTableView(VerifiedAccountMixin, ExportMixin, SingleTableMixin, TemplateView):
    class Table(RenderableTable):
        class Meta:
            attrs = GenericTable.Meta.attrs

        icon = tables.Column(orderable=False)
        name = tables.Column()
        beschreibung = tables.Column()
        ab_stufe = tables.Column()
        preis = tables.Column()
        art = tables.Column()
        other = tables.Column()

    table_class = Table

    template_name = "shop/show_all.html"

    export_name = "kompletter shop"
    exclude_columns = ["icon"]
    export_formats = ["csv", "json", "latex", "tsv"]

    # list of all table columns in class FullShopTableView.Table
    regular_table_columns = Table.base_columns.keys()

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        return super().get_context_data(
            **kwargs,
            topic="ganzer Shop",
            app_index="Shop",
            app_index_url=reverse("shop:index"),
            model_choices=[('', '--------'), *[(Model._meta.model_name, Model._meta.verbose_name) for Model in shopmodel_list]], # for filter of "art"
        )

    def get_table_data(self):
        """
        Return the table data that should be used to populate the rows.
        """
        if self.table_data is not None: return self.table_data


        # construct filters from query params. use only ones concerning table cols, ignoring page, ordering, etc.
        filters = {}
        for key, values in self.request.GET.items():
            if not next((True for col in self.regular_table_columns if key == col or key.startswith(f"{col}__")), False) or not values or not len(values): continue

            # number_fields are "ab_stufe", "preis"
            filters[key] = int(values) if key.startswith("ab_stufe") or key.startswith("preis") else values


        # get filtered objects
        objects = []
        for Model in shopmodel_list:

            # construct base queryset without frei_editierbare instances, apply user-filters and return objects as dicts in list
            objects += Model.objects\
                .prefetch_related("firmen")\
                .annotate(
                    model_name=Value(Model._meta.model_name),
                    art=Value(Model._meta.model_name),
                    art_display=Value(Model._meta.verbose_name),
                    **annotate_price(Model),
                    **annotate_other(Model, self.regular_table_columns),
                )\
                .filter(frei_editierbar=False, **filters)\
                .values()

        # return objects (manually ordered by name)
        return sorted(objects, key=lambda a: a["name"])


########################################################################
######################## by Category ###################################
########################################################################


####################### abstract base ##################################

shop_filter_fields = {
    "name": ["icontains"],
    "beschreibung": ["icontains"],
    "ab_stufe": ["lte"],
}


class ShopTableView(VerifiedAccountMixin, DynamicTableView):

    model = None
    filterset_class = None
    table_class = None
    custom_table_class = RenderableTable

    export_name = "<shop>"
    exclude_columns = ["icon"]
    export_formats = ["csv", "json", "latex", "tsv"]

    def get_export_filename(self, export_format):
        return super().get_export_filename(export_format).replace("<shop>", self.model._meta.verbose_name_plural)

    def get_queryset(self) -> QuerySet[Any]:
        return super().get_queryset().filter(frei_editierbar=False).prefetch_related("firmen").annotate(
            model_name=Value(self.model._meta.model_name),  # needed to render links at "name" cells
            **annotate_price(self.model),
            **annotate_other(self.model, self.get_table_class().base_columns.keys()),
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
        return reverse("shop:propose", args=[self.model])

    def get_table_class(self):
        """
        Return the class to use for the table.
        """
        if self.table_class:
            return self.table_class
        if self.model:
            has_fields_without_col = len([fieldname for fieldname in self.model.getShopDisplayFields() if fieldname not in self.table_fields]) > 0
            fields = (*self.table_fields, "other") if has_fields_without_col else self.table_fields

            return tables.table_factory(self.model, table=self.custom_table_class, fields=fields)

        name = type(self).__name__
        raise ImproperlyConfigured(f"You must either specify {name}.table_class or {name}.model")

    def get_filterset(self, filterset_class):
        filterset = super().get_filterset(filterset_class)

        # add non-model fields as filter. They are annotated in get_queryset()
        filterset.filters["preis__lte"] = NumberFilter(field_name="preis", lookup_expr='lte', label="Preis ist kleiner oder gleich")
        filterset.filters["other__icontains"] = CharFilter(field_name="other", lookup_expr='icontains', label="other enthält")

        return filterset





############################### views ########################################

class ItemTableView(ShopTableView):
    model = Item
    filterset_fields = shop_filter_fields
    table_fields = ("icon", "name", "beschreibung", "ab_stufe", "preis")


class WaffenWerkzeugeTableView(ShopTableView):
    model = Waffen_Werkzeuge
    filterset_fields = {
        **shop_filter_fields,
        "erfolge": ["icontains"],
        "bs": ["icontains"],
        "zs": ["icontains"],
        "dk": ["lte"],
        "schadensart": ["exact"]
    }
    table_fields = ("icon", "name", "beschreibung", "ab_stufe", "erfolge", "bs", "zs", "dk", "schadensart", "preis")


class MagazinTableView(ShopTableView):
    model = Magazin
    filterset_fields = {**shop_filter_fields, "schuss": ["exact"]}
    table_fields = ("icon", "name", "beschreibung", "ab_stufe", "schuss", "preis")


class PfeilBolzenTableView(ShopTableView):
    model = Pfeil_Bolzen
    filterset_fields = {**shop_filter_fields, "bs": ["icontains"], "zs": ["icontains"], "schadensart": ["exact"]}
    table_fields = ("icon", "name", "beschreibung", "ab_stufe", "bs", "zs", "schadensart", "preis")


class SchusswaffenTableView(ShopTableView):
    model = Schusswaffen
    filterset_fields = {
        **shop_filter_fields,
        "erfolge": ["exact"],
        "bs": ["icontains"],
        "zs": ["icontains"],
        "dk": ["exact"],
        "präzision": ["exact"],
        "schadensart": ["exact"]
    }
    table_fields = ("icon", "name", "beschreibung", "ab_stufe", "erfolge", "bs", "zs", "dk", "präzision", "schadensart", "preis")


class MagischeAusrüstungTableView(ShopTableView):
    model = Magische_Ausrüstung
    filterset_fields = shop_filter_fields
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

        stufe_1__lte = NumberFilter(field_name="stufe_1", lookup_expr="lte", label="Preis für Stufe 1 ist kleiner oder gleich")
        stufe_2__lte = NumberFilter(field_name="stufe_2", lookup_expr="lte", label="Preis für Stufe 2 ist kleiner oder gleich")
        stufe_3__lte = NumberFilter(field_name="stufe_3", lookup_expr="lte", label="Preis für Stufe 3 ist kleiner oder gleich")
        stufe_4__lte = NumberFilter(field_name="stufe_4", lookup_expr="lte", label="Preis für Stufe 4 ist kleiner oder gleich")
        stufe_5__lte = NumberFilter(field_name="stufe_5", lookup_expr="lte", label="Preis für Stufe 5 ist kleiner oder gleich")
        other__icontains = CharFilter(field_name="other", lookup_expr="icontains", label="other enthält")

    class Table(RenderableTable):
        class Meta(RenderableTable.Meta):
            pass

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
    custom_table_class = Table
    table_fields = ("icon", "name", "beschreibung", "ab_stufe", "stufe_1", "stufe_2", "stufe_3", "stufe_4", "stufe_5")


class RüstungTableView(ShopTableView):
    model = Rüstung
    filterset_fields = {
        **shop_filter_fields,
        "schutz": ["gte"],
        "härte": ["gte"],
        "haltbarkeit": ["gte"]
    }
    table_fields = ("icon", "name", "beschreibung", "ab_stufe", "schutz", "härte", "haltbarkeit",  "preis")


class AusrüstungTechnikTableView(ShopTableView):
    model = Ausrüstung_Technik
    filterset_fields = shop_filter_fields
    table_fields = ("icon", "name", "beschreibung", "ab_stufe", "preis")


class FahrzeugTableView(ShopTableView):
    model = Fahrzeug
    filterset_fields = {
        **shop_filter_fields,
        "schnelligkeit": ["gte"],
        "rüstung": ["gte"],
        "erfolge": ["lte"],
    }
    table_fields = ("icon", "name", "beschreibung", "ab_stufe", "schnelligkeit", "rüstung", "erfolge", "preis")


class EinbautenTableView(ShopTableView):
    model = Einbauten
    filterset_fields = {**shop_filter_fields, "manifestverlust": ["icontains"]}
    table_fields = ("icon", "name", "beschreibung", "ab_stufe", "manifestverlust", "preis")


class ZauberTableView(ShopTableView):
    model = Zauber
    filterset_fields = {
        **shop_filter_fields,
        "astralschaden": ["icontains"],
        "manaverbrauch": ["icontains"],
        "verteidigung": ["exact"],
        "kategorie": ["exact"],
        "schadensart": ["exact"]
    }
    table_fields = ("icon", "name", "beschreibung", "ab_stufe", "astralschaden", "manaverbrauch", "verteidigung", "schadensart", "kategorie", "preis")


class VergessenerZauberTableView(ShopTableView):
    model = VergessenerZauber
    filterset_fields = {
        **shop_filter_fields,
        "schaden": ["icontains"],
        "astralschaden": ["icontains"],
        "manaverbrauch": ["icontains"]
    }
    table_fields = ("icon", "name", "beschreibung", "ab_stufe", "schaden", "astralschaden", "manaverbrauch", "preis")


class AlchemieTableView(ShopTableView):
    model = Alchemie
    filterset_fields = shop_filter_fields
    table_fields = ("icon", "name", "beschreibung", "ab_stufe", "preis")


class TinkerTableView(ShopTableView):
    model = Tinker
    table_fields = ("icon", "name", "beschreibung", "ab_stufe", "werte")
    filterset_fields = {**shop_filter_fields, "werte": ["icontains"]}


class BegleiterTableView(ShopTableView):
    model = Begleiter
    filterset_fields = shop_filter_fields
    table_fields = ("icon", "name", "beschreibung", "ab_stufe", "preis")


class EngelsroboterTableView(ShopTableView):
    model = Engelsroboter
    filterset_fields = {
        **shop_filter_fields,
        'ST': ["gte"],
        'UM': ["gte"],
        'MA': ["gte"],
        'IN': ["gte"],
    }
    table_fields = ("icon", "name", "beschreibung", "ab_stufe", 'ST', 'UM', 'MA', 'IN', "preis")

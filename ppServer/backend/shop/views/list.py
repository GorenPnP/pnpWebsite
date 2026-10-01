from typing import Any, Dict

from django.apps import apps
from django.core.paginator import Paginator
from django.db.models import Max, Min, Value
from django.db.models.query import QuerySet
from django.shortcuts import reverse
from django.template import TemplateDoesNotExist, loader as TemplateLoader
from django.views.decorators.http import require_GET

from django_filters import NumberFilter, ChoiceFilter, Filter, OrderingFilter
from django_filters.filterset import filterset_factory
from django_filters.views import FilterView

from character.models import Charakter, Spieler
from ppServer.mixins import VerifiedAccountMixin

from ..forms import ShopFilter
from ..models import Fernkampfwaffe, Item, Tinker

####################### abstract base ##################################

shopmodel_list = [m for m in apps.get_app_config("shop").get_models() if not m._meta.abstract and m._meta.model_name not in ["modifier", "shopcategory", "tag", "upgrade"] and not m._meta.model_name.startswith("firma") and not m._meta.model_name.startswith("slot")]


shop_model_filter_fields = {
    "name": ["icontains"],
    "beschreibung": ["icontains"],
    "ab_stufe": ["lte"],
}
shop_extra_filter_fields = {
    "preis__lte": NumberFilter(field_name="preis", lookup_expr='lte', label="Preis ist kleiner oder gleich"),
}


class CharakterFilter(ChoiceFilter):
    ''' see shop->list.html that sets ab_stufe and price when char is selected '''

    def __init__(self, spieler: Spieler, *args, **kwargs):
        super().__init__(
            *args, **kwargs,
            label="für Charakter",
            choices=Charakter.objects.filter(larp=False, eigentümer=spieler).values_list("pk", "name"),
        )

    def filter(self, qs, value):
        # filter should already be set on selection in form. Selecting a character sets ab_stufe and price
        return qs


class ListView(VerifiedAccountMixin, FilterView):

    model = None
    filterset_fields = shop_model_filter_fields
    filterset_extra_fields = shop_extra_filter_fields

    page_size = 50    # num of items per page

    # topic/title of page and other stuff for the header & file export
    topic = None
    plus = None
    plus_url = None
    app_index = None
    app_index_url = None

    template_name = "shop/list.html"

    def setup(self, request, *args, **kwargs):
        self.model = self.model or kwargs["model"]
        res = super().setup(request, *args, **kwargs)

        return res

    def _update_context_data(self, context):

        # paginate (filtered, sorted) qs
        paginator = Paginator(context["filter"]._qs, self.page_size)  # paginate qs
        page_number = self.request.GET.get("page", 1)
        context["page_obj"] = paginator.get_page(page_number)

        return context


    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(
            *args, **kwargs,
            char_stats={c["pk"]: {"stufe": c["ep_stufe"], "geld": c["card__money"]} for c in Charakter.objects.filter(larp=False, eigentümer=self.request.spieler).values("pk", "ep_stufe", "card__money")},
            topic=self.get_topic(),
            plus=self.get_plus(),
            plus_url=self.get_plus_url(),
            app_index=self.get_app_index(),
            app_index_url=self.get_app_index_url(),
        )

        return self._update_context_data(context)

    def get_topic(self):
        if self.topic: return self.topic
        if self.model: return self.model._meta.verbose_name_plural or super().get_topic()

        return super().get_topic()

    def get_plus(self):
        if self.plus: return self.plus
        if self.model: return f"+ {self.model._meta.verbose_name}"

        return super().get_plus()

    def get_plus_url(self):
        if self.plus_url: return self.plus_url
        if self.model: return reverse("shop:propose", args=[self.model])
            
        return super().get_plus_url()

    def get_app_index(self):
        if self.app_index: return self.app_index
        if self.model: return self.model._meta.app_label.title()
        
        return None

    def get_app_index_url(self):
        if self.app_index_url: return reverse(self.app_index_url)
        if self.model: return reverse(f"{self.model._meta.app_label}:index")
        
        return None

    def get_filterset_extra_fields(self) -> Dict[str, Filter]:
        extra = self.filterset_extra_fields or {}

        return {
            **extra,
            "char": CharakterFilter(self.request.spieler),
            "o": OrderingFilter(fields=[*self.filterset_fields.keys(), *set([k.split("__")[0] for k in extra.keys()])]),
        }

    def get_item_template(self, model):
        """ uses model to return the url to a template as string to use for rendering an item in a list """

        model_name = model._meta.model_name
        template = 'shop/list_item/default.html'
        try:
            TemplateLoader.get_template(f'shop/list_item/{model_name}.html')
            template = f'shop/list_item/{model_name}.html'
        except TemplateDoesNotExist:
            pass
        return template

    def get_queryset(self) -> QuerySet[Any]:
        template = self.get_item_template(self.model)

        model_name = self.model._meta.model_name
        return super().get_queryset().filter(frei_editierbar=False).prefetch_related("firmen").annotate(
            template = Value(template),     # needed to render this item nicely

            preis = Min(f'firma{model_name}__preis'),
            max_preis = Max(f'firma{model_name}__preis'),
        ).order_by("name")

    def get_filterset_class(self):
        return filterset_factory(
            model=self.model if self.model else Item,
            filterset=ShopFilter,
            fields=self.filterset_fields
        )

    def get_filterset(self, filterset_class):
        filterset = super().get_filterset(filterset_class)

        # add non-model fields as filter. They are annotated in get_queryset()
        filterset.filters = {
            **filterset.filters,
            **self.get_filterset_extra_fields(),
        }

        return filterset

    @classmethod
    def as_view(cls, **initkwargs):
        return require_GET(super().as_view(**initkwargs))


class FernkampfwaffeView(ListView):
    model = Fernkampfwaffe

    def get_queryset(self) -> QuerySet[Any]:
        self.queryset = self.model.objects.annotate_schaden()
        return super().get_queryset()


class AllListView(ListView):
    topic = 'ganzer Shop'
    app_index = 'Shop'
    app_index_url = 'shop:index'
    model = Item    # irrelevant, just need a model here

    def get_plus(self):
        return None
    def get_plus_url(self):
        return None

    def _update_context_data(self, context):
        # add the correct (filtered, sorted) qs over the whole shop (except Tinker)
        
        # construct filters from query params. use only ones concerning table cols, ignoring page, ordering, etc.
        filters = {}
        for key, values in self.request.GET.items():
            if not next((True for col in self.filterset_fields if key == col or key.startswith(f"{col}__")), False) or not values or not len(values): continue

            # number_fields are "ab_stufe", "preis"
            filters[key] = int(values) if key.startswith("ab_stufe") or key.startswith("preis") else values

        sort_by = self.request.GET.get("o") or "name"

        # get filtered objects
        objects = []
        for Model in [m for m in shopmodel_list if m != Tinker]:
            template = self.get_item_template(Model)
            model_name = Model._meta.verbose_name

            qs = Model.objects.annotate_schaden() if Model == Fernkampfwaffe else Model.objects

            # construct base queryset without frei_editierbare instances, apply user-filters and return objects as dicts in list
            objects += qs\
                .prefetch_related("firmen")\
                .annotate(
                    template = Value(template),     # needed to render this item nicely
                    model_verbose_name = Value(model_name),

                    preis = Min(f'firma{Model._meta.model_name}__preis'),
                    max_preis = Max(f'firma{Model._meta.model_name}__preis'),
                )\
                .filter(frei_editierbar=False, **filters)\
                .order_by(sort_by)

        # sort objects (manually ordered by order-field or name)
        sorted_objects = sorted(objects, key=lambda a: getattr(a, sort_by.replace("-", "")), reverse=sort_by[0] == "-")

        # paginate (filtered, sorted) qs
        paginator = Paginator(sorted_objects, self.page_size)  # paginate qs
        page_number = self.request.GET.get("page", 1)
        context["page_obj"] = paginator.get_page(page_number)

        return context

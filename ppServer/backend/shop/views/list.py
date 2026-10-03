from typing import Any, Dict

from django.apps import apps
from django.db.models import Q, Count, Max, Min, OuterRef, Subquery, Value
from django.db.models.query import QuerySet
from django.shortcuts import reverse
from django.template import TemplateDoesNotExist, loader as TemplateLoader
from django.views.decorators.http import require_GET
from django.views.generic.list import ListView as DjangoListView

from django_filters import NumberFilter, ChoiceFilter, Filter, OrderingFilter
from django_filters.filterset import filterset_factory
from django_filters.views import FilterMixin

from character.models import Charakter, Spieler
from ppServer.mixins import VerifiedAccountMixin
from ppServer.utils import ConcatSubquery

from ..enums import category_enum
from ..forms import ShopFilter
from ..models import BaseShop, Fernkampfwaffe, Item, Modifier, Tinker

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


class HeaderMixin:
    ''' works well together with base/headed_main.html '''

    model = None

    # topic/title of page and other stuff for the header & file export
    topic = None
    plus = None
    plus_url = None
    app_index = None
    app_index_url = None

    def get_context_data(self, *args, **kwargs):
        return super().get_context_data(
            *args, **kwargs,
            topic=self.get_topic(),
            plus=self.get_plus(),
            plus_url=self.get_plus_url(),
            app_index=self.get_app_index(),
            app_index_url=self.get_app_index_url(),
        )

    def get_topic(self) -> str or None:
        if self.topic: return self.topic
        if self.model: return self.model._meta.verbose_name_plural or self.model._meta.verbose_name

        return None

    def get_plus(self) -> str or None:
        if self.plus: return self.plus
        if self.model: return f"+ {self.model._meta.verbose_name}"

        return None

    def get_plus_url(self) -> str or None:
        if self.plus_url: return self.plus_url
        if self.model: return reverse("shop:propose", args=[self.model])

        return None

    def get_app_index(self) -> str or None:
        if self.app_index: return self.app_index
        if self.model: return self.model._meta.app_label.title()

        return None

    def get_app_index_url(self) -> str or None:
        if self.app_index_url: return reverse(self.app_index_url)
        if self.model: return reverse(f"{self.model._meta.app_label}:index")

        return None


class ListFilterMixin(FilterMixin):
    
    # model = None
    filterset_fields = shop_model_filter_fields
    filterset_extra_fields = shop_extra_filter_fields

    def get_context_data(self, *args, **kwargs):

        return super().get_context_data(
            *args, **kwargs,
            **{
            # needed for CharacterFilter to work with .js in list.html to fill the other filter fields on selection
            "char_stats": {c["pk"]: {"stufe": c["ep_stufe"], "geld": c["card__money"]} for c in Charakter.objects.filter(larp=False, eigentümer=self.request.spieler).values("pk", "ep_stufe", "card__money")},
        })

    def get_filterset_extra_fields(self) -> Dict[str, Filter]:
        extra = self.filterset_extra_fields or {}

        return {
            **extra,
            "char": CharakterFilter(self.request.spieler),
            "o": OrderingFilter(fields=[*self.filterset_fields.keys(), *set([k.split("__")[0] for k in extra.keys()])]),
        }

    def get_filterset(self, filterset_class):
        filterset = super().get_filterset(filterset_class)

        # add non-model fields as filter. They are annotated in get_queryset()
        filterset.filters = {
            **filterset.filters,
            **self.get_filterset_extra_fields(),
        }

        return filterset

    def get_filterset_class(self):
        return filterset_factory(
            model=self.model if self.model else None,
            filterset=ShopFilter,
            fields=self.filterset_fields
        )

    # NOTE GET is a View thing...
    def get(self, request, *args, **kwargs):
        '''
        this prevents the class-based view (or others downstream) from executing their .get().
        Luckily, django's ListView handles pagination in .get_context_data() too, based on self.object_list or self.get_queryset().
        This function uses get_queryset() of the underlying view to construct its Filter. After filtering and sorting,
        it assigns the result back to self.object_list, so the underlying view can paginate it if needed.
        '''

        filterset_class = self.get_filterset_class()
        self.filterset = self.get_filterset(filterset_class)

        if (
            not self.filterset.is_bound
            or self.filterset.is_valid()
            or not self.get_strict()
        ):
            self.object_list = self.filterset.qs
        else:
            self.object_list = self.filterset.queryset.none()

        context = self.get_context_data(filter=self.filterset)
        return self.render_to_response(context)


class MixedListFilterMixin(ListFilterMixin):
    def get_queryset(self) -> QuerySet[Any]:
        return self.model.objects.none()

    def get_filters(self):
        
        # get all possible filter(names) from the class. Ignores ordering, char (and page)
        filterset_filters = {k: v for k, v in self.get_filterset(self.get_filterset_class()).filters.items() if k not in self.get_filterset_extra_fields().keys()}
        # needed to cast string values to int()
        number_fields = [k for k, v in filterset_filters.items() if type(v) == NumberFilter]

        # construct filters from query params (^= request.GET). use only ones concerning filterset_fields, ignoring page, ordering, etc.
        filters = {}
        for key, values in self.request.GET.items():
            if key not in filterset_filters or not values or not len(values): continue

            # number_fields are "ab_stufe", "preis"
            filters[key] = int(values) if key in number_fields else values

        return {"frei_editierbar": False, **filters}

    def set_ordering(self):
        ''' set self.ordering according to the filter data in request.GET '''

        self.ordering = self.request.GET.get("o") or "name"

    def get_objects(self, filters: dict) -> list[BaseShop]:
        ''' get all shop items (except Tinker), filter and sort them '''

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
                .filter(**filters)\
                .order_by(self.ordering)

        # sort objects (manually ordered by order-field or name)
        return sorted(objects, key=lambda a: getattr(a, self.ordering.replace("-", "")), reverse=self.ordering[0] == "-")

    # NOTE GET is a View thing...
    def get(self, request, *args, **kwargs):
        '''
        this prevents the class-based view (or others downstream) from executing their .get().
        Luckily, django's ListView handles pagination in .get_context_data() too, based on self.object_list or self.get_queryset().
        This function uses get_queryset() of the underlying view to construct its Filter. After filtering and sorting,
        it assigns the result back to self.object_list, so the underlying view can paginate it if needed.
        '''
        filters = self.get_filters()
        self.set_ordering()
        self.object_list = self.get_objects(filters)

        filterset_class = self.get_filterset_class()
        self.filterset = self.get_filterset(filterset_class)
        context = self.get_context_data(filter=self.filterset)

        return self.render_to_response(context)


class BaseList(DjangoListView):
    ''' needs to set self.model in url or manually '''

    model = None
    paginate_by = 50    # num of objects per page
    context_object_name = "object_list"

    template_name = "shop/list.html"

    def setup(self, request, *args, **kwargs):
        self.model = self.model or kwargs["model"]
        res = super().setup(request, *args, **kwargs)

        return res

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

        def modifiers(model: type[BaseShop]):
            # get Category letter of Shop-model
            catLetter = next((letter for letter, cat in category_enum if cat == model._meta.verbose_name_plural), '')

            return ConcatSubquery(
                Modifier.objects\
                    .annotate(
                        num_firmen = Count('firmen'),
                        num_cats = Count('kategorien'),
                    )\
                    .filter(active=True)\
                    .filter(
                        # get category-specific modifiers with correct firma OR category
                        Q(firmen__in=OuterRef("firmen")) | Q(kategorien__kategorie=catLetter) |
                        # get base modifiers (that modify everything)
                        (Q(num_firmen = 0) & Q(num_cats = 0))
                    )\
                    .values("factor")
            )

            # CALC: floor(price * exp(sum(ln(n), ln(n1), ...)) + .5)

        model_name = self.model._meta.model_name
        qs = super().get_queryset().filter(frei_editierbar=False).prefetch_related("firmen").annotate(
            template = Value(template),     # needed to render this item nicely

            # TODO
            # modifiers = modifiers(self.model),
            preis = Min(f'firma{model_name}__preis'),
            max_preis = Max(f'firma{model_name}__preis'),
        ).order_by("name")

        print(qs.first().modifiers)

        return qs

    @classmethod
    def as_view(cls, **initkwargs):
        return require_GET(super().as_view(**initkwargs))




class ListView(VerifiedAccountMixin, HeaderMixin, ListFilterMixin, BaseList):
    pass

class FernkampfwaffeView(ListView):
    model = Fernkampfwaffe

    def get_queryset(self) -> QuerySet[Any]:
        self.queryset = self.model.objects.annotate_schaden()
        return super().get_queryset()


class AllListView(VerifiedAccountMixin, HeaderMixin, MixedListFilterMixin, BaseList):
    topic = 'ganzer Shop'
    app_index = 'Shop'
    app_index_url = 'shop:index'
    model = Item    # irrelevant, just need a model here for the filter

    def get_plus(self):
        return None     # ignore preset with self.model
    def get_plus_url(self):
        return None     # ignore preset with self.model

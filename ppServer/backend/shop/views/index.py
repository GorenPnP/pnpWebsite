from django.contrib import messages
from django.shortcuts import redirect
from django.views.decorators.http import require_GET
from django.urls import NoReverseMatch, reverse

from django.views.generic import TemplateView

from base.views import reviewable_shop
from ppServer.mixins import SpielleitungOnlyMixin, VerifiedAccountMixin

from ..forms import get_ProposeForm
from ..models import *
from .list import AllListView, BaseList, HeaderMixin, ListView, MixedListFilterMixin, shopmodel_list


def get_list_url(m: type[BaseShop]) -> str:
    try:
        return reverse(f'shop:{m._meta.model_name}_list')
    except NoReverseMatch:
        return reverse('shop:list', args=[m])


class ReviewView(VerifiedAccountMixin, SpielleitungOnlyMixin, HeaderMixin, MixedListFilterMixin, BaseList):
    # template_name = "shop/review.html"
    topic = "Neue Items"
    app_index = 'Shop'
    app_index_url = 'shop:index'
    model = Item    # irrelevant, just need a model here for the filter
    filterset_fields = {}

    def get_plus(self):
        return None     # ignore preset with self.model
    def get_plus_url(self):
        return None     # ignore preset with self.model

    def set_ordering(self):
        self.ordering = "name"

    def get_filters(self):
        return {"frei_editierbar": True}

    def get_filterset_extra_fields(self):
        return {}


class IndexView(VerifiedAccountMixin, HeaderMixin, MixedListFilterMixin, BaseList):
    template_name = "shop/index.html"
    topic = "Shop"

    model = Item
    paginate_by = 6

    def get_filters(self):
        # filter items on sale
        return {"frei_editierbar": False}

    def set_ordering(self):
        self.ordering = "-discount"

    def get_objects(self, filters):

        # add interesting items per model
        self.sections = []
        for m in shopmodel_list:
            if m._meta.model_name == "tinker": continue

            self.sections.append({
                "link": get_list_url(m),
                "text": m._meta.verbose_name_plural,
                "object_list": m.objects.annotate_price().filter(**filters).order_by(self.ordering)[:self.paginate_by]
            })

        return super().get_objects(filters)

    def get_context_data(self, *args, **kwargs):
        return super().get_context_data(
            *args, **kwargs, 
            links = self.sections,
        )


class ProposeView(VerifiedAccountMixin, TemplateView):
    template_name = "shop/propose.html"

    def setup(self, request, *args, **kwargs):
        res = super().setup(request, *args, **kwargs)
        self.model = self.kwargs["model"]
        return res

    def get_context_data(self, *args, **kwargs):
        return super().get_context_data(*args, **kwargs, **{
        "topic": "neues Item",
        "app_index": self.model._meta.verbose_name_plural,
        "app_index_url": get_list_url(self.model),
    })

    def get(self, request, *args, **kwargs):
        form = get_ProposeForm(self.model)()
        return super().get(request, *args, **kwargs, form=form)

    def post(self, *args, **kwargs):
        form = get_ProposeForm(self.model)(self.request.POST)
        form.full_clean()
        if form.is_valid():
            item = form.save()
            messages.success(self.request, "Vorschlag wurde eingereicht")
            return redirect(get_list_url(self.model))

        messages.error(self.request, "Beim Speichern sind Fehler aufgetreten")

        return super().get(*args, **kwargs, form=form)

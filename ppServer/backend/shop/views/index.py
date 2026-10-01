from django.contrib import messages
from django.shortcuts import redirect
from django.views.decorators.http import require_GET
from django.urls import NoReverseMatch, reverse

from django.views.generic import TemplateView

from base.views import reviewable_shop
from ppServer.mixins import SpielleitungOnlyMixin, VerifiedAccountMixin

from ..forms import get_ProposeForm
from ..models import *
from .list import ListView, shopmodel_list


def get_list_url(m: type[BaseShop]) -> str:
    try:
        return reverse(f'shop:{m._meta.model_name}_list')
    except NoReverseMatch:
        return reverse('shop:list', args=[m])


class ReviewView(SpielleitungOnlyMixin, ListView):
    template_name = "shop/review.html"
    model = Item

    def get_template_names(self):
        return [self.template_name]

    def get_topic(self):
        return "Neue Items"

    def get_plus(self):
        return None
    def get_plus_url(self):
        return None

    def _update_context_data(self, context):
        return context

    def get_queryset(self):
        objects = []
        
        # get objects (manually ordered by name)
        for e in sorted(reviewable_shop(), key=lambda e: e["item"]["name"]):
            item = e["item"]
            model = e["model"]
            template = self.get_item_template(model)

            display = {"kategorie": None, "schadensart": None, "händigkeit": None}
            for field in display.keys():
                if field in item and item[field]:
                    for k, v in model._meta.get_field(field).choices:
                        if k == item[field]:
                            display[field] = v
                            break

            objects.append({
                **item,
                **{f'get_{field}_display': v for field,v in display.items()},
                "template": template,     # needed to render this item nicely
                "model_verbose_name": model._meta.verbose_name,
                "detail_url": reverse('admin:shop_{}_change'.format(model._meta.model_name), args=(item["id"],)),
            })
        return objects

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(*args, **kwargs, object_list=self.get_queryset())

        if not context["object_list"]: return redirect("base:index")
        return self.render_to_response(context)


class IndexView(VerifiedAccountMixin, TemplateView):
    template_name = "shop/index.html"

    @classmethod
    def as_view(cls, **initkwargs):
        return require_GET(super().as_view(**initkwargs))

    def get_context_data(self, *args, **kwargs):
        return super().get_context_data(
            *args, **kwargs, 
            topic = "Shop",
            links = [{"link": get_list_url(m), "text": m._meta.verbose_name_plural} for m in shopmodel_list if m._meta.model_name != "tinker"],
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

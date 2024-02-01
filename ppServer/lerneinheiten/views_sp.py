import json
from typing import Any

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models.query import QuerySet
from django.shortcuts import redirect
from django.views.decorators.http import require_POST
from django.views.generic import DetailView
from django.views.generic.list import ListView
from django.shortcuts import reverse, get_object_or_404

from ppServer.decorators import spielleiter_only
from ppServer.mixins import SpielleiterOnlyMixin

from .forms import *
from .models import *

class EditorIndexView(LoginRequiredMixin, SpielleiterOnlyMixin, ListView):
    model = Einheit
    template_name = "lerneinheiten/sp/editor_index.html"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        return super().get_context_data(
            **kwargs,
            topic = "Editor",
            # app_index = "Charaktere",
            # app_index_url = reverse("character:index"),

            new_einheit_form = EinheitForm(),
            edit_einheit_forms = [{"id": einheit["pk"], "form": EinheitForm(initial=einheit)} for einheit in Einheit.objects.values("pk", *EinheitForm._meta.fields)],
            new_page_forms = [{"id": einheit_id, "form": PageForm(initial={"einheit": einheit_id})} for einheit_id in Einheit.objects.values_list("pk", flat=True)],
        )

    def get_queryset(self) -> QuerySet[Any]:
        return super().get_queryset()\
            .prefetch_related("page_set", "fach")
    
    def post(self, *args, **kwargs):
        orders: dict = json.loads(self.request.POST.get("id_order"))

        einheiten = []
        pages = []
        for id, sub_ids in orders.items():

            # sort einheiten
            if id in [0, "0"]:
                for index, einheit_id in enumerate(sub_ids):
                    einheit = get_object_or_404(Einheit, id=einheit_id)
                    einheit.number = index+1
                    einheiten.append(einheit)
                continue

            # sort pages
            for index, page_id in enumerate(sub_ids):
                page = get_object_or_404(Page, id=page_id)
                page.number = index+1
                pages.append(page)

        Einheit.objects.bulk_update(einheiten, fields=["number"])
        Page.objects.bulk_update(pages, fields=["number"])
        messages.success(self.request, "Reihenfolge wurde gespeichert")

        return redirect("lerneinheiten:editor_index")


class EditorPageView(LoginRequiredMixin, SpielleiterOnlyMixin, DetailView):
    model = Page
    template_name = "lerneinheiten/sp/editor_page/_default.html"

    def get_template_names(self) -> list[str]:
        return [f"lerneinheiten/sp/editor_page/{self.object.get_type_display().lower()}.html"] + super().get_template_names()

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(
            **kwargs,
            app_index = "Editor",
            app_index_url = reverse("lerneinheiten:editor_index"),
        )
        context["topic"] = context["object"].__str__()
        context["form"] = PageUpdateForm(instance=context["object"])

        return context
    
    def post(self, request, pk: int, **kwargs):
        object = get_object_or_404(self.model, pk=pk)

        if "content" in request.POST:
            object.content = json.loads(request.POST.get("content"))
            object.save(update_fields=["content"])
            messages.success(request, "Content wurde erfolgreich gespeichert")
            return redirect(request.build_absolute_uri())

        form = PageUpdateForm(request.POST, instance=object)
        form.full_clean()
        if form.is_valid():
            form.save()
            messages.success(request, "Settings wurden erfolgreich gespeichert")
        else:
            messages.error(request, "Settings konnten nicht gespeichert werden")

        return redirect(request.build_absolute_uri())


@require_POST
@login_required
@spielleiter_only()
def edit_einheit(request, pk: int):
    einheit = get_object_or_404(Einheit, pk=pk)

    form = EinheitForm(request.POST, instance=einheit)
    form.full_clean()
    if form.is_valid():
        form.save()
        messages.success(request, "Änderungen wurden gespeichert")
    else:
        messages.error(request, "Änderungen konnten nicht gespeichert werden")

    return redirect("lerneinheiten:editor_index")

@require_POST
@login_required
@spielleiter_only()
def new_einheit(request):
    form = EinheitForm(request.POST)
    form.full_clean()
    if form.is_valid():
        form.save()
        messages.success(request, "Einheit wurde angelegt")
    else:
        messages.error(request, "Einheit konnte nicht angelegt werden")

    return redirect("lerneinheiten:editor_index")

@require_POST
@login_required
@spielleiter_only()
def new_page(request):
    form = PageForm(request.POST)
    form.full_clean()
    if form.is_valid():
        form.save()
        messages.success(request, "Seite wurde angelegt")
    else:
        messages.error(request, "Seite konnte nicht angelegt werden")

    return redirect("lerneinheiten:editor_index")
    

# TODO: save ordering if changed and something else is POSTed
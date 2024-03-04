import json
from typing import Any

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models.query import QuerySet
from django.http.response import JsonResponse
from django.shortcuts import get_object_or_404, redirect, reverse
from django.views.decorators.http import require_POST
from django.views.generic import DetailView
from django.views.generic.list import ListView

from ppServer.decorators import spielleiter_only
from ppServer.mixins import SpielleiterOnlyMixin

from .forms import *
from .models import *

class EditorIndexView(LoginRequiredMixin, SpielleiterOnlyMixin, ListView):
    model = Einheit
    template_name = "lerneinheiten/sp/editor/index.html"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        return super().get_context_data(
            **kwargs,
            topic = "Editor",
            app_index = "LARP",
            app_index_url = reverse("lerneinheiten:index"),

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
    template_name = "lerneinheiten/sp/editor/_default.html"

    def get_template_names(self) -> list[str]:
        return [f"lerneinheiten/sp/editor/{self.object.get_type_display().lower()}.html"] + super().get_template_names()

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

        form = PageUpdateForm(request.POST, instance=object)
        form.full_clean()
        if form.is_valid():
            form.save()
            messages.success(request, "Änderungen wurden erfolgreich gespeichert")
        else:
            messages.error(request, "Änderungen konnten nicht gespeichert werden")

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

@require_POST
@login_required
@spielleiter_only()
def image_upload(request, page_id):
    try:
        page = Page.objects.get(pk=page_id)
    except Page.DoesNotExist:
        error_dict = {'message': 'Page not found.'}
        return JsonResponse(error_dict, status=404)

    uploaded_file = request.FILES['file']
    image = PageImage.objects.create(image=uploaded_file, page=page)

    response_dict = {
        'message': 'File uploaded successfully!',
        'uri': image.image.url
    }

    return JsonResponse(response_dict, status=200)
    

# TODO: save ordering if changed and something else is POSTed
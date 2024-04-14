import json
from typing import Any

from django.contrib import messages
from django.db.models.query import QuerySet
from django.shortcuts import redirect
from django.views.decorators.http import require_POST
from django.views.generic import DetailView
from django.views.generic.list import ListView
from django.shortcuts import reverse

from ppServer.decorators import LARPler_only, verified_account
from ppServer.mixins import LARPlerOnlyMixin, VerifiedAccountMixin

from .forms import InquiryForm, SpielerPageForm
from .models import *


class IndexView(VerifiedAccountMixin, LARPlerOnlyMixin, ListView):
    model = Einheit
    template_name = "lerneinheiten/spieler/index.html"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        return super().get_context_data(
            **kwargs,
            topic = "LARP",
        )

    def get_queryset(self) -> QuerySet[Any]:
        return super().get_queryset()\
            .prefetch_related("page_set", "fach")


class PageView(VerifiedAccountMixin, LARPlerOnlyMixin, DetailView):
    model = Page
    template_name = "lerneinheiten/spieler/page/_default.html"

    def get_template_names(self) -> list[str]:
        return [f"lerneinheiten/spieler/page/{self.object.get_type_display().lower()}.html"] + super().get_template_names()

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(
            **kwargs,
            app_index = "LARP",
            app_index_url = reverse("lerneinheiten:index"),
        )
        context["topic"] = context["object"].__str__()

        # add spieler's answer
        sp_page = SpielerPage.objects.filter(spieler=self.request.spieler.instance, page=context["object"]).first()
        context["form"] = SpielerPageForm(instance=sp_page)

        # add inquiry form
        inquiry = context["object"].inquiry_set.filter(spieler=self.request.spieler.instance).first()
        context["inquiry"] = inquiry
        if inquiry is not None:
            context["inquiry_form"] = InquiryForm(instance=inquiry)
        else:
            context["inquiry_form"] = InquiryForm(initial = {
                "page": context["object"],
                "spieler": self.request.spieler.instance,
            })

        return context
    
    def get_queryset(self) -> QuerySet[Any]:
        return super().get_queryset().prefetch_related("einheit")
    
    def post(self, request, *args, **kwargs):
        page = self.get_object()
        sp_page = SpielerPage.objects.filter(spieler=request.spieler.instance, page=page).first()

        # zeichnen
        requestPOST = request.POST
        if page.type == "uc":

            # delete obsolete images
            if sp_page:
                PageImage.objects.filter(page=page, spielerPage=sp_page).delete()

            # create new images
            drawn_image = PageImage.objects.create(image=request.FILES['answer_drawn'], page=page)
            bg_image = PageImage.objects.create(image=request.FILES['answer_bg'], page=page)
            
            # construct/update Page fields
            answer = {
                "drawn": drawn_image.image.url,
                "bg": bg_image.image.url,
            }
            requestPOST = request.POST.__copy__()
            requestPOST.__setitem__("answer", json.dumps(answer))


        form = SpielerPageForm(requestPOST, instance=sp_page)
        form.full_clean()
        if form.is_valid():
            object = form.save(commit=False)
            object.spieler = request.spieler.instance
            object.page = page
            object.save()

            # zeichnen (Rückrichtung imgs -> object)
            if page.type == "uc":
                drawn_image.spielerPage = object
                bg_image.spielerPage = object
                drawn_image.save(update_fields=["spielerPage"])
                bg_image.save(update_fields=["spielerPage"])

            messages.success(request, "Antwort erfolgreich gespeichert")
        else:
            messages.error(request, "Antwort konnte nicht gespeichert werden")

        return redirect(request.build_absolute_uri())



@require_POST
@verified_account
@LARPler_only
def inquiry_form(request, page_id: int):
    form = InquiryForm(request.POST, instance=Inquiry.objects.filter(page__id=page_id, spieler=request.spieler.instance).first())

    form.full_clean()
    if form.is_valid():
        form.save()
        messages.success(request, "Feedback wurde angelegt")
    else:
        messages.error(request, "Feedback konnte nicht angelegt werden")

    return redirect(reverse("lerneinheiten:page", args=[page_id]))
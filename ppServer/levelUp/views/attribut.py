from django.db.models import F, Sum, Value
from django.contrib import messages
from django.http.request import HttpRequest
from django.http.response import HttpResponse
from django.shortcuts import redirect
from django.utils.decorators import method_decorator

from django_tables2.columns import TemplateColumn

from base.abstract_views import DynamicTableView, GenericTable
from character.models import RelAttribut

from ..decorators import is_erstellung_done
from ..mixins import LevelUpMixin
from ..views import get_required_aktuellerWert


@method_decorator([is_erstellung_done], name="dispatch")
class GenericAttributView(LevelUpMixin, DynamicTableView):

    BASE_AKTUELL = "aktuell"
    BASE_MAX = "max"
    class Table(GenericTable):
        BASE_AKTUELL = "aktuell"
        BASE_MAX = "max"

        class Meta:
            model = RelAttribut
            fields = ["attribut__titel", "aktuell_ap", "max_ap", "result"]
            attrs = GenericTable.Meta.attrs

        aktuell_ap = TemplateColumn(template_name="levelUp/_number_input.html", extra_context={"add_field": "aktuellerWert", "bonus_field": "aktuellerWert_bonus", "input_field": "aktuellerWert_temp", "max_field": "aktuell_limit", "base_name": BASE_AKTUELL, "base_class": BASE_AKTUELL, "dataset_id": "dataset_id"})
        max_ap = TemplateColumn(template_name="levelUp/_number_input.html", extra_context={"add_field": "maxWert", "bonus_field": None, "input_field": "maxWert_temp", "max_field": None, "base_name": BASE_MAX, "base_class": BASE_MAX, "dataset_id": "dataset_id"})

        def render_attribut__titel(self, value, record):
            return f"{value} ({record.attribut.beschreibung})"

        def render_result(self, value, record):
            curr = (record.aktuellerWert or 0) + (record.aktuellerWert_temp or 0) + (record.aktuellerWert_bonus or 0)
            max = (record.maxWert or 0) + (record.maxWert_temp or 0)
            return f"{curr} / {max}"


    topic = "Attribute"
    template_name = "levelUp/ap.html"
    model = RelAttribut

    table_class = Table


    def get_queryset(self):
        char = self.get_character()

        return RelAttribut.objects.prefetch_related("char").filter(char=char).annotate(
            aktuell_limit = F("maxWert") + F("maxWert_temp") - F("aktuellerWert"),
            result=Value(1), # override later
            dataset_id=F("attribut__id")
        )


    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        char = self.get_character()

        # collect values
        ap = {}
        ap_spent = 0
        for relattr in self.get_queryset():
            attr = relattr.attribut

            # get & sanitize
            aktuell = int(request.POST.get(f"{self.BASE_AKTUELL}-{attr.id}"))
            max = int(request.POST.get(f"{self.BASE_MAX}-{attr.id}"))
            if relattr.aktuellerWert + aktuell > relattr.maxWert + max:
                messages.error(request, f"Bei {attr} ist der Wert höher als das Maximum")

            min_aktuell = get_required_aktuellerWert(char, attr.titel)
            if relattr.aktuellerWert + relattr.aktuellerWert_bonus + aktuell < min_aktuell:
                messages.error(request, f"Im {attr}-Pool musst du mindestens {min_aktuell} haben, weil du das für deine verteilten FP/FG brauchst")


            # save in temporal datastructure
            ap[attr.id] = {
                "aktuell": aktuell,
                "max": max,
            }
            ap_spent += aktuell + 2* max

        # test them
        ap_max = self.get_queryset()\
            .prefetch_related("attribut")\
            .aggregate(
                spent = Sum("aktuellerWert_temp") + 2* Sum("maxWert_temp")
            )["spent"] + char.ap

        if ap_spent > ap_max:
            messages.error(request, "Du hast zu wenig AP")

        # all fine or not?
        if len(messages.get_messages(request)):
            return redirect(request.build_absolute_uri())

        # apply them to db
        char.ap = ap_max - ap_spent
        char.save(update_fields=["ap"])

        relattrs = []
        for relattr in RelAttribut.objects.prefetch_related("attribut").filter(char=char):
            relattr.aktuellerWert_temp = ap[relattr.attribut.id]["aktuell"]
            relattr.maxWert_temp = ap[relattr.attribut.id]["max"]
            relattrs.append(relattr)
        RelAttribut.objects.bulk_update(relattrs, ["aktuellerWert_temp", "maxWert_temp"])

        # return response
        messages.success(request, "Erfolgreich gespeichert")
        return redirect(request.build_absolute_uri())


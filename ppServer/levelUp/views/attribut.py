import sys

from django.db import models
from django.db.models import F, Sum, Value, Case, When
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

        aktuell_ap = TemplateColumn(template_name="levelUp/_number_input.html", extra_context={"add_field": "aktuell_base", "bonus_field": "aktuell_bonus", "input_field": "aktuell_temp", "max_field": "aktuell_limit", "base_name": BASE_AKTUELL, "base_class": BASE_AKTUELL, "dataset_id": "dataset_id", "text": None, "disabled": "is_aktuell_fix"})
        max_ap = TemplateColumn(template_name="levelUp/_number_input.html", extra_context={"add_field": "max_base", "bonus_field": None, "input_field": "max_temp", "max_field": "max_limit", "base_name": BASE_MAX, "base_class": BASE_MAX, "dataset_id": "dataset_id", "text": None, "disabled": "is_max_fix"})

        def render_attribut__titel(self, value, record):
            return f"{value} ({record.attribut.beschreibung})"

        def render_result(self, value, record):
            return f"{record.aktuell()} / {record.max()}"


    topic = "Attribute"
    template_name = "levelUp/ap.html"
    model = RelAttribut

    table_class = Table

    INITIAL_AP_PENALTY_AKTUELL = 1
    INITIAL_AP_PENALTY_MAX = 1


    def get_queryset(self):
        char = self.get_character()

        return RelAttribut.objects.prefetch_related("char").filter(char=char).annotate(
            is_aktuell_fix=Case(When(aktuellerWert_fix=None, then=False), default=True, output_field=models.BooleanField()),
            is_max_fix=Case(When(maxWert_fix=None, then=False), default=True, output_field=models.BooleanField()),

            aktuell_base = Case(When(is_aktuell_fix=False, then=F("aktuellerWert")), default=F("aktuellerWert_fix"), output_field=models.IntegerField()),
            max_base = Case(When(is_max_fix=False, then=F("maxWert")), default=F("maxWert_fix"), output_field=models.IntegerField()),

            aktuell_bonus = Case(When(is_aktuell_fix=False, then=F("aktuellerWert_bonus")), default=None, output_field=models.IntegerField()),

            aktuell_temp = Case(When(is_aktuell_fix=False, then=F("aktuellerWert_temp")), default=0, output_field=models.IntegerField()),
            max_temp = Case(When(is_max_fix=False, then=F("maxWert_temp")), default=0, output_field=models.IntegerField()),

            aktuell_limit = Case(When(is_aktuell_fix=False, then=F("maxWert") + F("maxWert_temp") - F("aktuellerWert")), default=0, output_field=models.IntegerField()),
            max_limit = Case(When(is_max_fix=False, then=sys.maxsize), default=0, output_field=models.IntegerField()),

            result=Value(1), # override later
            dataset_id=F("attribut__id"),
        )

    def get_context_data(self, *args, **kwargs):
        return super().get_context_data(*args, **kwargs,
            INITIAL_AP_PENALTY_AKTUELL=self.INITIAL_AP_PENALTY_AKTUELL,
            INITIAL_AP_PENALTY_MAX=self.INITIAL_AP_PENALTY_MAX,
        )

    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        char = self.get_character()

        # collect values
        ap = {}
        ap_spent = 0
        ap_max = char.ap
        for relattr in self.get_queryset():
            attr = relattr.attribut

            # get & sanitize
            aktuell = int(request.POST.get(f"{self.BASE_AKTUELL}-{attr.id}") or "0")
            max = int(request.POST.get(f"{self.BASE_MAX}-{attr.id}") or "0")
            if relattr.aktuellerWert + aktuell > relattr.maxWert + max:
                messages.error(request, f"Bei {attr} ist der Wert höher als das Maximum")

            min_aktuell = get_required_aktuellerWert(char, attr.titel)
            if relattr.aktuellerWert + relattr.aktuellerWert_bonus + aktuell < min_aktuell:
                messages.error(request, f"Im {attr}-Pool musst du mindestens {min_aktuell} haben, weil du das für deine verteilten FP/FG brauchst")


            # save in temporary datastructure
            ap[attr.id] = {
                "aktuell": aktuell,
                "max": max,
            }

            # calc spent ap ..

            # .. previously
            ap_max += relattr.aktuellerWert_temp + 2* relattr.maxWert_temp
            if relattr.aktuellerWert_temp and not relattr.aktuellerWert: ap_max += self.INITIAL_AP_PENALTY_AKTUELL
            if relattr.maxWert_temp and not relattr.maxWert: ap_max += self.INITIAL_AP_PENALTY_MAX

            # .. now
            ap_spent += aktuell + 2* max
            if aktuell and not relattr.aktuellerWert: ap_spent += self.INITIAL_AP_PENALTY_AKTUELL
            if max and not relattr.maxWert: ap_spent += self.INITIAL_AP_PENALTY_MAX

        # test them
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


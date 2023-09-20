from django.db.models import F, Subquery, OuterRef, Sum, Value, Window
from django.contrib import messages
from django.http.request import HttpRequest
from django.http.response import HttpResponse
from django.shortcuts import redirect
from django.utils.decorators import method_decorator
from django.utils.html import format_html

from django_tables2.columns import TemplateColumn

from base.abstract_views import DynamicTableView, GenericTable
from character.models import *

from ..decorators import is_erstellung_done
from ..mixins import LevelUpMixin


@method_decorator([is_erstellung_done], name="dispatch")
class GenericFertigkeitView(LevelUpMixin, DynamicTableView):

    class Table(GenericTable):

        class Meta:
            model = RelFertigkeit
            fields = ["fertigkeit__titel", "attribut", "fp", "fg", "pool"]
            attrs = GenericTable.Meta.attrs
            row_attrs = {
                "class": lambda record: "impro_possible" if record["impro_possible"] else ""
            }

        fp = TemplateColumn(template_name="levelUp/_number_input.html", extra_context={"add_field": "fp", "bonus_field": "fp_bonus", "input_field": "fp_temp", "max_field": "fp_limit", "base_name": "fp", "base_class": "fp", "dataset_id": "id", "text": None})
        fg = TemplateColumn(template_name="levelUp/_number_input.html", extra_context={"add_field": "fg", "bonus_field": None, "input_field": "fg_temp", "max_field": None, "base_name": "fg", "base_class": "fg", "dataset_id": "gruppe_id", "text": "gruppe"})



    topic = "Fertigkeiten"
    template_name = "levelUp/fert.html"
    model = RelFertigkeit

    table_class = Table
    table_pagination = False


    def get_table_data(self):
        char = self.get_character()

        attrs = {attr.attribut.titel: attr.aktuell() for attr in RelAttribut.objects.prefetch_related("char", "attribut").filter(char=char)}
        gruppen = {gruppe.gruppe: {"fg": gruppe.fg, "fg_temp": gruppe.fg_temp} for gruppe in RelGruppe.objects.prefetch_related("char").filter(char=char)}

        qs = RelFertigkeit.objects\
            .prefetch_related("char", "fertigkeit__attribut")\
            .filter(char=char)\
            .annotate(
                impro_possible = F("fertigkeit__impro_possible"),    # replace later
                attribut = F("fertigkeit__attribut__titel"),    # replace later
                gruppe_id=F("fertigkeit__gruppe")    # important for html-form
            )\
            .values("id", "fertigkeit__titel", "gruppe_id", "attribut", "fp", "fp_temp", "fp_bonus", "impro_possible")
        
        for entry in qs:
            aktuell = attrs[entry['attribut']]

            entry["fg"] = gruppen[entry["gruppe_id"]]["fg"]
            entry["fg_temp"] = gruppen[entry["gruppe_id"]]["fg_temp"]
            entry["fp_limit"] = aktuell - entry["fp"]
            entry["attribut"] = format_html(f"{entry['attribut']} (<span class='attr_sum'>{aktuell}</span>)")

            entry["pool"] = sum([aktuell, entry["fg"], entry["fg_temp"], entry["fp"], entry["fp_temp"], entry["fp_bonus"]])
            entry["gruppe"] = [name for token, name in enums.gruppen_enum if token == entry["gruppe_id"]][0]

        return qs

    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        char = self.get_character()

        #### collect values ####
        # fp
        fp = {}
        for relfert in char.relfertigkeit_set.all():
            fert = relfert.fertigkeit

            # get & sanitize
            attrs = {attr.attribut.titel: attr.aktuell() for attr in RelAttribut.objects.prefetch_related("char", "attribut").filter(char=char)}
            rel_fp = int(request.POST.get(f"fp-{relfert.id}") or 0)
            if rel_fp > attrs[relfert.fertigkeit.attribut.titel] - relfert.fp:
                messages.error(request, f"Bei {fert} sind die FP höher als erlaubt")

            # save in temporal datastructure
            fp[fert.id] = rel_fp

        # fg
        fg = {}
        for relgruppe in RelGruppe.objects.filter(char=char):
            gruppe = relgruppe.gruppe

            # get & sanitize

            ## fg
            temp_fg = [int(fg) for fg in request.POST.getlist(f"fg-{gruppe}") if fg.isnumeric()]
            all_equal = len(temp_fg) == 0 or False not in [fg == temp_fg[0] for fg in temp_fg]
            if not all_equal:
                messages.error(request, f"Bei {relgruppe.get_gruppe_display()} sind die FG der einzelnen Fertigkeiten nicht gleich")
                return redirect(request.build_absolute_uri())

            rel_fg = int(temp_fg[0]) if len(temp_fg) else 0  # getting array of (max. 3) identical because html contains 3 with similar "name" attrs
            # TODO
            # if rel_fg > relattr.aktuellerWert + relattr.aktuellerWert_bonus + relattr.aktuellerWert_temp - relattr.fg:
            #     messages.error(request, f"Bei {attr} sind die FG höher als erlaubt")

            # save in temporal datastructure
            fg[gruppe] = rel_fg

        #### test them ####
        # fp
        fp_max = RelFertigkeit.objects.filter(char=char).aggregate(
                spent = Sum("fp_temp")
            )["spent"] + char.fp

        if sum(fp.values()) > fp_max:
            messages.error(request, "Du hast zu wenig FP")

        # fg
        fg_max = RelGruppe.objects.filter(char=char).aggregate(
                spent = Sum("fg_temp")
            )["spent"] + char.fg

        if sum(fg.values()) > fg_max:
            messages.error(request, "Du hast zu wenig FG")

        #### all fine or not? ####
        if len(messages.get_messages(request)):
            return redirect(request.build_absolute_uri())

        #### apply them to db ###
        char.fp = fp_max - sum(fp.values())
        char.fg = fg_max - sum(fg.values())
        char.save(update_fields=["fp", "fg"])

        relgruppen = []
        for relgruppe in RelGruppe.objects.prefetch_related("char").filter(char=char):
            relgruppe.fg_temp = fg[relgruppe.gruppe]
            relgruppen.append(relgruppe)
        RelGruppe.objects.bulk_update(relgruppen, ["fg_temp"])
        
        relferts = []
        for relfert in RelFertigkeit.objects.prefetch_related("fertigkeit", "char").filter(char=char):
            relfert.fp_temp = fp[relfert.fertigkeit.id]
            relferts.append(relfert)
        RelFertigkeit.objects.bulk_update(relferts, ["fp_temp"])

        # return response
        messages.success(request, "Erfolgreich gespeichert")
        return redirect(request.build_absolute_uri())
from django.db.models import F, Subquery, OuterRef, Q, Count, Sum, Value, Window, Func
from django.contrib import messages
from django.http.request import HttpRequest
from django.http.response import HttpResponse
from django.shortcuts import redirect
from django.utils.decorators import method_decorator
from django.utils.html import format_html

from django_tables2.columns import TemplateColumn

from base.abstract_views import DynamicTablesView, GenericTable
from character.models import *

from ..decorators import is_erstellung_done
from ..mixins import LevelUpMixin


@method_decorator([is_erstellung_done], name="dispatch")
class GenericFertigkeitView(LevelUpMixin, DynamicTablesView):

    class Table1(GenericTable):

        class Meta:
            model = RelFertigkeit
            fields = ["fertigkeit__titel", "attribute", "fp", "fg", "pool"]
            attrs = GenericTable.Meta.attrs

        fp = TemplateColumn(template_name="levelUp/_number_input.html", extra_context={"add_field": "fp", "bonus_field": "fp_bonus", "input_field": "fp_temp", "max_field": "fp_limit", "base_name": "fp", "base_class": "fp", "dataset_id": "id"})
        fg = TemplateColumn(template_name="levelUp/_number_input.html", extra_context={"add_field": "fg", "bonus_field": None, "input_field": "fg_temp", "max_field": "fg_limit", "base_name": "fg", "base_class": "fg", "dataset_id": "attr_dataset_id"})

        def render_attribute(self, value, record):
            # like SCH (1)
            return format_html(f"{record.fertigkeit.attr1.titel} (<span class='attr_sum'>{record.attr_sum}</span>)")

        def render_pool(self, value, record):
            return record.attr_sum + record.fg + record.fg_temp + record.fp + record.fp_temp + record.fp_bonus

    class TableElse(GenericTable):
        class Meta:
            model = RelFertigkeit
            fields = ["fertigkeit__titel", "attribute", "fp", "pool"]
            attrs = GenericTable.Meta.attrs

        fp = TemplateColumn(template_name="levelUp/_number_input.html", extra_context={"add_field": "fp", "bonus_field": "fp_bonus", "input_field": "fp_temp", "max_field": "fp_limit", "base_name": "fp", "base_class": "fp", "dataset_id": "id"})

        def render_attribute(self, value, record):
            # like SCH + IN (1)
            return format_html(f"{record.fertigkeit.attr1.titel} + {record.fertigkeit.attr2.titel} (<span class='attr_sum'>{record.attr_sum}</span>)")

        def render_pool(self, value, record):
            return record.attr_sum + record.fp + record.fp_bonus


    topic = "Fertigkeiten"
    template_name = "levelUp/fert.html"
    model = RelFertigkeit

    tables = [Table1, TableElse]
    table_pagination = False


    def get_queryset(self):
        char = self.get_character()

        # will be a subquery for all (1 or 2) NewCharakterAttributes related to NewCharakterFertigkeit by fertigkeit.attr1 & fertigkeit.attr2
        attr_qs = RelAttribut.objects.prefetch_related("char")\
            .filter(char=char)\
            .filter(Q(attribut=OuterRef("fertigkeit__attr1")) | Q(attribut=OuterRef("fertigkeit__attr2")))\
            .annotate(
            aktuell = F("aktuellerWert") + F("aktuellerWert_bonus") + F("aktuellerWert_temp"),
            fg_limit = F("aktuell") - F("fg"),
        )

        return RelFertigkeit.objects\
            .prefetch_related("char", "fertigkeit", "fertigkeit__attr1", "fertigkeit__attr2")\
            .filter(char=char)\
            .annotate(
                # get num of attributes. Can be 1 or 2.
                attribut_count = Subquery(attr_qs.annotate(attribute_count = Window(
                    expression=Count("*")
                )).values("attribute_count")[:1]),

                # sum the aktuell of related attributes
                attr_sum = Subquery(attr_qs.annotate(
                    sum=Window( expression=Sum('aktuell') ),
                ).values('sum')[:1]),


                # handle fg, fg_temp. Only relevant for those with 1 attribute.
                fg = Subquery(attr_qs.annotate(
                    sum=Window( expression=Sum('fg') ),
                ).values('sum')[:1]),
                fg_temp = Subquery(attr_qs.annotate(
                    sum=Window( expression=Sum('fg_temp') ),
                ).values('sum')[:1]),

                # calc limits. Round normally.
                fp_limit = Func((F("attr_sum") *1.0) / F("attribut_count"), function='ROUND') - F("fp"),
                fg_limit = Subquery(attr_qs.annotate(
                    sum=Window( expression=Sum('fg_limit') ),
                ).values('sum')[:1]),

                attribute = Value("some name"),    # replace later
                pool = Value(1),    # replace later

                # important for html-form
                attr_dataset_id=F("fertigkeit__attr1__id")
            )


    def get_tables_data(self):
        qs = self.get_queryset().prefetch_related("fertigkeit__attr1", "fertigkeit__attr2")

        return [
            qs.filter(fertigkeit__attr2__isnull=True),
            qs.filter(fertigkeit__attr2__isnull=False)
        ]


    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        char = self.get_character()

        #### collect values ####
        # fp
        fp = {}
        for relfert in self.get_queryset():
            fert = relfert.fertigkeit

            # get & sanitize
            rel_fp = int(request.POST.get(f"fp-{relfert.id}") or 0)
            if rel_fp > relfert.fp_limit:
                messages.error(request, f"Bei {fert} sind die FP höher als erlaubt")

            # save in temporal datastructure
            fp[fert.id] = rel_fp

        # fg
        fg = {}
        for relattr in RelAttribut.objects.filter(char=char):
            attr = relattr.attribut

            # get & sanitize

            ## fg
            temp_fg = [int(fg) for fg in request.POST.getlist(f"fg-{attr.id}") if fg.isnumeric()]
            all_equal = len(temp_fg) == 0 or False not in [fg == temp_fg[0] for fg in temp_fg]
            if not all_equal:
                messages.error(request, f"Bei {attr} sind die FG der einzelnen Fertigkeiten nicht gleich")
                return redirect(request.build_absolute_uri())

            rel_fg = int(temp_fg[0]) if len(temp_fg) else 0  # getting array of (max. 3) identical because html contains 3 with similar "name" attrs
            if rel_fg > relattr.aktuellerWert + relattr.aktuellerWert_bonus + relattr.aktuellerWert_temp - relattr.fg:
                messages.error(request, f"Bei {attr} sind die FG höher als erlaubt")

            # save in temporal datastructure
            fg[attr.id] = rel_fg

        #### test them ####
        # fp
        fp_max = self.get_queryset().aggregate(
                spent = Sum("fp_temp")
            )["spent"] + char.fp

        if sum(fp.values()) > fp_max:
            messages.error(request, "Du hast zu wenig FP")

        # fg
        fg_max = RelAttribut.objects.filter(char=char).aggregate(
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

        relattrs = []
        for relattr in RelAttribut.objects.prefetch_related("attribut", "char").filter(char=char):
            relattr.fg_temp = fg[relattr.attribut.id]
            relattrs.append(relattr)
        RelAttribut.objects.bulk_update(relattrs, ["fg_temp"])
        
        relferts = []
        for relfert in RelFertigkeit.objects.prefetch_related("fertigkeit", "char").filter(char=char):
            relfert.fp_temp = fp[relfert.fertigkeit.id]
            relferts.append(relfert)
        RelFertigkeit.objects.bulk_update(relferts, ["fp_temp"])

        # return response
        messages.success(request, "Erfolgreich gespeichert")
        return redirect(request.build_absolute_uri())
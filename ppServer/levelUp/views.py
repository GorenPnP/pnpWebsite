from functools import cmp_to_key
import re
from typing import Any, Dict

from django.db.models import F, Subquery, OuterRef, Q, Count, Sum, Value, Window, Func, Exists
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http.request import HttpRequest
from django.http.response import HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.views.generic.base import TemplateView
from django.urls import reverse
from django.utils.html import format_html

import django_tables2 as tables
from django_tables2.columns import TemplateColumn

from ppServer.mixins import VerifiedAccountMixin

from base.abstract_views import DynamicTableView, DynamicTablesView, GenericTable
from character.models import *
from shop.models import Zauber

from .forms import PersonalForm, AffektivitätForm
from .mixins import OwnCharakterMixin


class HeaderMixin:
    topic = None
    plus = None
    plus_url = None
    app_index = None
    app_index_url = None

    def get_dataset_kwargs(self):
        return {"title": self.topic}.update(self.dataset_kwargs or {})

    def get_topic(self):
        return self.topic or self.model._meta.verbose_name_plural or None

    def get_plus(self):
        return self.plus or None
    
    def get_plus_url(self):
        return reverse(self.plus_url) if self.plus_url else None
    
    def get_app_index(self):
        if self.app_index: return self.app_index
        return self.model._meta.app_label.title() if self.model else None

    def get_app_index_url(self):
        if self.app_index_url: return reverse(self.app_index_url)
        return reverse(f"{self.model._meta.app_label}:index") if self.model else None

    def get_context_data(self, *args, **kwargs):
        return super().get_context_data(*args, **kwargs,
            topic=self.get_topic(),
            plus=self.get_plus(),
            plus_url=self.get_plus_url(),
            app_index=self.get_app_index(),
            app_index_url=self.get_app_index_url(),
        )


def get_required_aktuellerWert(char: Charakter, attr_titel: str) -> int:
    ''' get min aktuellerWert of attr__titel by current fp, fg '''

    # get attr aktuell
    attribute = {rel.attribut.titel: rel.aktuell for rel in RelAttribut.objects.filter(char=char).annotate(aktuell = F("aktuellerWert") + F("aktuellerWert_temp") + F("aktuellerWert_bonus"))}

    # check with fp
    base_relfert_qs = RelFertigkeit.objects.prefetch_related("fertigkeit__attr1", "fertigkeit__attr2").filter(char=char)

    one_attr_fert = base_relfert_qs.filter(fertigkeit__attr1__titel=attr_titel, fertigkeit__attr2=None).annotate(sum=F("fp") + F("fp_temp"))\
            .aggregate(Max("sum"))["sum__max"] or 0

    two_attr_fert_1 = base_relfert_qs.exclude(fertigkeit__attr2=None).filter(fertigkeit__attr1__titel=attr_titel).annotate(
        sum=F("fp") + F("fp_temp"),
        attr_titel=F("fertigkeit__attr2__titel")
    )
    two_attr_fert_2 = base_relfert_qs.exclude(fertigkeit__attr2=None).filter(fertigkeit__attr2__titel=attr_titel).annotate(
        sum=F("fp") + F("fp_temp"),
        attr_titel=F("fertigkeit__attr1__titel")
    )
    needed_in_two_attr_ferts = []
    for rel in list([*two_attr_fert_1, *two_attr_fert_2]):
        if (attribute[attr_titel] + attribute[rel.attr_titel]) % 2 == 0:
            needed_in_two_attr_ferts.append(2 * rel.sum - attribute[rel.attr_titel])
        else:
            needed_in_two_attr_ferts.append(2 * rel.sum - attribute[rel.attr_titel] -1)


    # check fg
    fg = RelAttribut.objects.filter(char=char, attribut__titel=attr_titel).annotate(sum=F("fg") + F("fg_temp")).values("sum")[0]["sum"]

    # calc max of all
    return max(one_attr_fert, fg, *needed_in_two_attr_ferts)


class GenericAttributView(LoginRequiredMixin, OwnCharakterMixin, DynamicTableView):

    def get_character(self) -> Charakter: raise NotImplementedError()


    BASE_AKTUELL = "aktuell"
    BASE_MAX = "max"
    class Table(GenericTable):
        BASE_AKTUELL = "aktuell"
        BASE_MAX = "max"

        class Meta:
            model = RelAttribut
            fields = ["attribut__titel", "aktuell_ap", "max_ap", "result"]
            attrs = GenericTable.Meta.attrs

        aktuell_ap = TemplateColumn(template_name="levelUp/_number_input.html", extra_context={"add_field": "aktuell", "max_field": "aktuell_limit", "base_name": BASE_AKTUELL, "base_class": BASE_AKTUELL, "dataset_id": "dataset_id"})
        max_ap = TemplateColumn(template_name="levelUp/_number_input.html", extra_context={"add_field": "max","max_field": None, "base_name": BASE_MAX, "base_class": BASE_MAX, "dataset_id": "dataset_id"})

        def render_attribut__titel(self, value, record):
            return f"{value} ({record.attribut.beschreibung})"

        def render_result(self, value, record):
            curr = (record.aktuell or 0) + (record.aktuell_ap or 0)
            max = (record.max or 0) + (record.max_ap or 0)
            return f"{curr} / {max}"


    topic = "Attribute"
    template_name = "levelUp/ap.html"
    model = RelAttribut

    table_class = Table


    def get_queryset(self):
        char = self.get_character()

        return RelAttribut.objects.prefetch_related("char").filter(char=char).annotate(
            aktuell = F("aktuellerWert") + F("aktuellerWert_bonus"),
            aktuell_ap = F("aktuellerWert_temp"),
            aktuell_limit = F("maxWert") + F("maxWert_bonus") + F("maxWert_temp") - F("aktuellerWert") - F("aktuellerWert_bonus"),
            max = F("maxWert") + F("maxWert_bonus"),
            max_ap = F("maxWert_temp"),
            result=Value(1), # override later
            dataset_id=F("attribut__id")
        )

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context["char"] = context["object_list"][0].char
        return context

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
            if relattr.aktuell + aktuell > relattr.max + max:
                messages.error(request, f"Bei {attr} ist der Wert höher als das Maximum")

            min_aktuell = get_required_aktuellerWert(char, attr.titel)
            if relattr.aktuell + aktuell < min_aktuell:
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
                spent = Sum("aktuell_ap") + 2* Sum("max_ap")
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
        for relattr in RelAttribut.objects.prefetch_related("attribut", "char").filter(char=char):
            relattr.aktuellerWert_temp = ap[relattr.attribut.id]["aktuell"]
            relattr.maxWert_temp = ap[relattr.attribut.id]["max"]
            relattrs.append(relattr)
        RelAttribut.objects.bulk_update(relattrs, ["aktuellerWert_temp", "maxWert_temp"])

        # return response
        messages.success(request, "Erfolgreich gespeichert")
        return redirect(request.build_absolute_uri())


class GenericFertigkeitView(LoginRequiredMixin, OwnCharakterMixin, DynamicTablesView):
    
    def get_character(self) -> Charakter: raise NotImplementedError()


    class Table1(GenericTable):

        class Meta:
            model = RelFertigkeit
            fields = ["fertigkeit__titel", "attribute", "fp", "fg", "pool"]
            attrs = GenericTable.Meta.attrs

        fp = TemplateColumn(template_name="levelUp/_number_input.html", extra_context={"add_field": "fp_bonus", "max_field": "fp_limit", "base_name": "fp", "base_class": "fp", "dataset_id": "id"})
        fg = TemplateColumn(template_name="levelUp/_number_input.html", extra_context={"add_field": "fg_bonus", "max_field": "fp_limit", "base_name": "fg", "base_class": "fg", "dataset_id": "attr_dataset_id"})

        def render_attribute(self, value, record):
            # like SCH (1)
            return format_html(f"{record.fertigkeit.attr1.titel} (<span class='attr_sum'>{record.attr_sum}</span>)")

        def render_pool(self, value, record):
            return record.attr_sum + record.fg + record.fg_bonus + record.fp + record.fp_bonus

    class TableElse(GenericTable):
        class Meta:
            model = RelFertigkeit
            fields = ["fertigkeit__titel", "attribute", "fp", "pool"]
            attrs = GenericTable.Meta.attrs

        fp = TemplateColumn(template_name="levelUp/_number_input.html", extra_context={"add_field": "fp_bonus", "max_field": "fp_limit", "base_name": "fp", "base_class": "fp", "dataset_id": "id"})

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
            aktuell = F("aktuellerWert") + F("aktuellerWert_bonus") + F("aktuellerWert_temp")
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

                # calc limit for the fp. Round normally.
                fp_limit = Func((F("attr_sum") *1.0) / F("attribut_count"), function='ROUND'),


                # handle fg, fg_bonus. Only releveant for those with 1 attribute.
                fg = Subquery(attr_qs.annotate(
                    sum=Window( expression=Sum('fg') ),
                ).values('sum')[:1]),
                fg_bonus = Subquery(attr_qs.annotate(
                    sum=Window( expression=Sum('fg_bonus') ),
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


    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context["char"] = context["object_list"][0].char
        return context


    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        char = self.get_character()

        #### collect values ####
        # fp
        fp = {}
        for relfert in self.get_queryset():
            fert = relfert.fertigkeit

            # get & sanitize
            rel_fp = int(request.POST.get(f"fp-{relfert.id}"))
            if rel_fp > relfert.fp_limit:
                messages.error(request, f"Bei {fert} sind die FP höher als erlaubt")

            # save in temporal datastructure
            fp[fert.id] = rel_fp

        # fg
        fg = {}
        for relattr in RelAttribut.objects.filter(char=char):
            attr = relattr.attribut

            # get & sanitize
            rel_fg = int(request.POST.getlist(f"fg-{attr.id}")[0])  # getting array of 3 identical because html contains 3 with similar "name" attrs
            if rel_fg + relfert.fg_bonus > relattr.aktuellerWert + relattr.aktuellerWert_bonus + relattr.aktuellerWert_temp:
                messages.error(request, f"Bei {attr} sind die FG höher als erlaubt")

            # save in temporal datastructure
            fg[attr.id] = rel_fg

        #### test them ####
        # fp
        fp_max = self.get_queryset().aggregate(
                spent = Sum("fp")
            )["spent"] + char.fp

        if sum(fp.values()) > fp_max:
            messages.error(request, "Du hast zu wenig FP")

        # fg
        fg_max = RelAttribut.objects.filter(char=char).aggregate(
                spent = Sum("fg")
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
            relattr.fg = fg[relattr.attribut.id]
            relattrs.append(relattr)
        RelAttribut.objects.bulk_update(relattrs, ["fg"])
        
        relferts = []
        for relfert in RelFertigkeit.objects.prefetch_related("fertigkeit", "char").filter(char=char):
            relfert.fp = fp[relfert.fertigkeit.id]
            relferts.append(relfert)
        RelFertigkeit.objects.bulk_update(relferts, ["fp"])

        # return response
        messages.success(request, "Erfolgreich gespeichert")
        return redirect(request.build_absolute_uri())


def sort_teils(a, b):
    if len(a["rel"]) and not len(b["rel"]): return -1
    if not len(a["rel"]) and len(b["rel"]): return 1

    return -1 if a["titel"] <= b["titel"] else 1

class GenericTeilView(LoginRequiredMixin, OwnCharakterMixin, HeaderMixin, TemplateView):
    template_name = "levelUp/teil/teil.html"

    def get_character(self) -> Charakter: raise NotImplementedError()


    def get_context_data(self, *args, **kwargs) -> Dict[str, Any]:
        char = self.get_character()
        situations = ["i", "e"] if char.in_erstellung else ["i", "n"]

        teil_fields = ["id", "titel", "beschreibung", "needs_ip", "needs_attribut", "needs_fertigkeit", "needs_engelsroboter", "needs_notiz", "ip", "min_ip", "max_ip", "is_sellable", "max_amount"]

        # TODO: let sellable sell, but not buy new if in campaign


        # all RelTeils
        # all Teils that are choosable right now
        displayed_teils = list(
            self.Model.objects
                .filter(Q(wann_wählbar__in=situations))
                .values(*teil_fields)
        )
        displayed_teils_dict = {teil["id"]: teil for teil in displayed_teils}
        for teil in displayed_teils_dict.values():
            teil["rel"] = []
            teil["is_buyable"] = True


        for rel in self.RelModel.objects.prefetch_related("teil").filter(char=char):
            if rel.teil.id in displayed_teils_dict:

                displayed_teils_dict[rel.teil.id]["rel"].append(rel)

            else:
                displayed_teils_dict[rel.teil.id] = {
                    **{field: getattr(rel.teil, field) for field in teil_fields},
                    "rel": [rel],
                    "is_buyable": False
                }

        # properties of every entry: is_buyable?
        for teil in displayed_teils_dict.values():
            teil["is_buyable"] = teil["is_buyable"] and (not teil["max_amount"] or teil["max_amount"] > len(teil["rel"]))


        context = super().get_context_data(*args, **kwargs,
            is_vorteil = self.is_vorteil,
            object_list = sorted(displayed_teils_dict.values(), key=cmp_to_key(sort_teils)),

            attribute = Attribut.objects.all(),
            fertigkeiten = Fertigkeit.objects.all(),
            engelsroboter = Engelsroboter.objects.all()
        )
        # create or override -> don't cause 'get_context_data() got multiple values for keyword argument 'char''
        context["char"] = char
        return context

    def post(self, request, *args, **kwargs):

        changes = {key:value for (key,value) in request.POST.items() if value}
        char = self.get_character()
        ip = 0

        ####### no updates of existing RelModel possible #########

        # handle deletions

        # TODO check if deletion is allowed for the char

        deletions = [int(re.search(r'\d+$', key).group(0)) for key in changes.keys() if "delete" in key]
        qs_deletions = self.RelModel.objects.filter(id__in=deletions, char=char, is_sellable=True)
        ip = self.calc_ip_on_deletion(ip, sum([rel.ip if rel.teil.needs_ip else rel.teil.ip for rel in qs_deletions.prefetch_related("teil")]))
        qs_deletions.delete()


        # handle changes
        # [(teil_id, rel_id), (...), ...]
        updates = [(int(re.findall(r'\d+', key)[0]), int(re.findall(r'\d+', key)[1])) for key in request.POST.keys() if "change" in key]
        for teil_id, rel_id in updates:
            try:
                own_rel = self.RelModel.objects.get(id=rel_id, teil__id=teil_id, char=char)
            except: continue


            if f"ip-{teil_id}-{rel_id}" in request.POST:
                own_rel.ip = int(request.POST.get(f"ip-{teil_id}-{rel_id}"))

            if f"attribut-{teil_id}-{rel_id}" in request.POST:
                own_rel.attribut_id = int(request.POST.get(f"attribut-{teil_id}-{rel_id}"))

            if f"fertigkeit-{teil_id}-{rel_id}" in request.POST:
                own_rel.fertigkeit_id = int(request.POST.get(f"fertigkeit-{teil_id}-{rel_id}"))

            if f"engelsroboter-{teil_id}-{rel_id}" in request.POST:
                own_rel.engelsroboter_id = int(request.POST.get(f"engelsroboter-{teil_id}-{rel_id}"))

            if f"notizen-{teil_id}-{rel_id}" in request.POST:
                own_rel.notizen = request.POST.get(f"notizen-{teil_id}-{rel_id}")

            own_rel.save()


        # handle additions

        # TODO check if addition is allowed for the char

        additions = [int(re.search(r'\d+$', key).group(0)) for key in changes.keys() if "add" in key]
        changes = {key:value for (key,value) in changes.items() if "delete" not in key and "add" not in key}

        for teil_id in additions:
            fields = {(k.replace(f"-{teil_id}", '')): v for (k, v) in changes.items() if f"-{teil_id}" in k}
            teil = self.Model.objects.get(id=teil_id)

            # amount
            if teil.max_amount and teil.max_amount <= self.RelModel.objects.filter(char=char, teil=teil).count():
                messages.error(request, f"Maximale Anzahl von {teil.titel} überschritten")
                continue

            # ip
            if teil.needs_ip and "ip" not in fields.keys():
                messages.error(request, f"IP fehlen für {teil.titel}")
                continue

            # Attribut
            if teil.needs_attribut:
                try:
                    fields["attribut"] = Attribut.objects.get(id=fields["attribut"])
                except:
                    messages.error(request, f"Das Attribut fehlt für {teil.titel}")
                    continue

            # Fertigkeit
            if teil.needs_fertigkeit:
                try:
                    fields["fertigkeit"] = Fertigkeit.objects.get(id=fields["fertigkeit"])
                except:
                    messages.error(request, f"Die Fertigkeit fehlt für {teil.titel}")
                    continue

            # Engelsroboter
            if teil.needs_engelsroboter:
                try:
                    fields["engelsroboter"] = Engelsroboter.objects.get(id=fields["engelsroboter"])
                except:
                    messages.error(request, f"Der Engelsroboter fehlt für {teil.titel}")
                    continue

            # Notizen
            if teil.needs_notiz and "notizen" not in fields.keys():
                messages.error(request, f"Notizen fehlen für {teil.titel}")
                continue

            # create relation
            self.RelModel.objects.create(teil=teil, char=char, is_sellable=teil.is_sellable, **fields)
            ip = self.calc_ip_on_creation(ip, teil.ip if not teil.needs_ip else int(fields["ip"]))


        # apply ip
        char.ip += ip
        char.save()

        return redirect(request.build_absolute_uri())

class GenericNachteilView(GenericTeilView):
    topic = "Nachteile"
    RelModel = RelNachteil
    Model = Nachteil
    is_vorteil = False

    def calc_ip_on_creation(self, ip, ip_of_teil) -> int:
        return ip + ip_of_teil
    
    def calc_ip_on_deletion(self, ip, ip_of_teil) -> int:
        return ip - ip_of_teil

class GenericVorteilView(GenericTeilView):
    topic = "Vorteile"
    RelModel = RelVorteil
    Model = Vorteil
    is_vorteil = True

    def calc_ip_on_creation(self, ip, ip_of_teil) -> int:
        return ip - ip_of_teil
    
    def calc_ip_on_deletion(self, ip, ip_of_teil) -> int:
        return ip + ip_of_teil


class GenericZauberView(LoginRequiredMixin, OwnCharakterMixin, HeaderMixin, TemplateView):
    
    def get_character(self) -> Charakter: raise NotImplementedError()

    template_name = "levelUp/zauber.html"
    topic = "Zauber"


    def get_context_data(self, *args, **kwargs):
        char = self.get_character()
        rel_ma = RelAttribut.objects.get(char=char, attribut__titel='MA')
        zauberplätze = char.zauberplätze if char.zauberplätze else {}
        max_stufe = max([int(k) for k in zauberplätze.keys()], default=-1)
        zauber = Zauber.objects\
                .filter(frei_editierbar=False, ab_stufe__lte=max_stufe)\
                .exclude(id__in=char.zauber.values("id"))\
                .values("id", "name")
        
        for z in zauber:
            z["geld"] = min([f.getPrice() for f in FirmaZauber.objects.filter(item__id=z["id"])])

        context = super().get_context_data(*args, **kwargs,
            own_zauber = RelZauber.objects.filter(char=char).order_by("item__name"),
            zauber = zauber,

            MA_aktuell = rel_ma.aktuellerWert + rel_ma.aktuellerWert_temp - get_required_aktuellerWert(char, "MA"),
            free_slots = sum(zauberplätze.values()),
            get_tier_cost_with_sp = get_tier_cost_with_sp(),
        )
        # create or override -> don't cause 'get_context_data() got multiple values for keyword argument 'char''
        context["char"] = char
        return context


    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        char = self.get_character()
        operation = request.POST.get("operation")

        if operation == "create":
            zauber_id = request.POST.get("zauber_id")
            zauber = get_object_or_404(Zauber, id=zauber_id)
            
            # checks
            if RelZauber.objects.filter(char=char, item=zauber).exists():
                messages.error(request, f"Den Zauber {zauber.name} kennst du bereits.")
                return redirect(request.build_absolute_uri())

            min_stufe_of_slots = min([int(z) for z in char.zauberplätze.keys() if int(z) >= zauber.ab_stufe], default=-1)
            if min_stufe_of_slots == -1:
                messages.error(request, f"Du hast keinen passenden Zauberplatz für {zauber.name}.")
                return redirect(request.build_absolute_uri())
            
            price = min([t.getPrice() for t in FirmaZauber.objects.filter(item=zauber)])
            if not char.in_erstellung and char.geld < price:
                messages.error(request, f"Du hast nicht genug Geld für {zauber.name}.")
                return redirect(request.build_absolute_uri())


            # apply
            # zauberplätze
            char.zauberplätze[str(min_stufe_of_slots)] -= 1
            if char.zauberplätze[str(min_stufe_of_slots)] == 0:
                del char.zauberplätze[str(min_stufe_of_slots)]
            # geld
            if not char.in_erstellung: char.geld -= price
            char.save(update_fields=["zauberplätze", "geld"])

            RelZauber.objects.create(char=char, item=zauber)
            return redirect(request.build_absolute_uri())

        if operation == "update":
            # GATHER DATA
            rel_zauber_ids = [int(id) for id in request.POST.keys() if id.isnumeric()]

            new_tiers = {id: int(request.POST.get(str(id))) for id in rel_zauber_ids}
            rel_zauber = RelZauber.objects.filter(char=char, id__in=rel_zauber_ids)


            # PERFORM CHECKS

            # char already has zauber
            if rel_zauber.count() != len(rel_zauber_ids):
                messages.error(request, "Du wolltest Tier zu Zaubern vergeben, die du gar nicht kennst")
                return redirect(request.build_absolute_uri())

            for rel in rel_zauber:
                # not lower than current value
                if rel.tier > new_tiers[rel.id]:
                    messages.error(request, "Du kannst Tier nicht wieder verkaufen")
                    return redirect(request.build_absolute_uri())
                
                # has to be lower than max_tier
                if rel.tier > char.max_tier_allowed():
                    messages.error(request, f"Du kannst Tier nicht über {char.max_tier_allowed()} steigern")
                    return redirect(request.build_absolute_uri())


            if request.POST.get("payment_method") == "slot":

                # char has enough zauberplätze to pay for
                num_slots_char = sum(char.zauberplätze.values())
                num_slots_new_tier = sum(new_tiers.values()) - rel_zauber.aggregate(tier_sum=Sum("tier"))["tier_sum"]
                if num_slots_char < num_slots_new_tier:
                    messages.error(request, f"Du hast mehr neue Tier gewählt als du Zauberplätze hast")
                    return redirect(request.build_absolute_uri())


                # APPLY

                # pay <num_slots_new_tier> many zauberplätze
                while num_slots_new_tier > 0:
                    min_stufe = min([int(k) for k in char.zauberplätze.keys()])
                    diff = min(char.zauberplätze[str(min_stufe)], num_slots_new_tier)

                    num_slots_new_tier -= diff
                    if char.zauberplätze[str(min_stufe)] == diff:
                        del char.zauberplätze[str(min_stufe)]
                    else:
                        char.zauberplätze[str(min_stufe)] -= diff

                char.save(update_fields=["zauberplätze"])


            if request.POST.get("payment_method") == "sp":
                sp = 0
                for rel in rel_zauber:
                    new_tier = new_tiers[rel.id]
                    existing_tier = rel.tier
                    while new_tier > existing_tier:
                        sp += get_tier_cost_with_sp()[new_tier]
                        new_tier -= 1

                # char has enough sp to pay for
                if char.sp < sp:
                    messages.error(request, "Du hast zu wenig SP")
                    return redirect(request.build_absolute_uri())


                # pay SP
                char.sp -= sp
                char.save(update_fields=["sp"])

            if request.POST.get("payment_method") == "ap":
                rel_ma = get_object_or_404(RelAttribut, char=char, attribut__titel="MA")
                
                ap_available = char.ap + rel_ma.aktuellerWert + rel_ma.aktuellerWert_temp - get_required_aktuellerWert(char, "MA")
                ap_to_pay = sum(new_tiers.values()) - rel_zauber.aggregate(tier_sum=Sum("tier"))["tier_sum"]


                # char has enough AP/MA.aktuellerWert to pay for
                if ap_available < ap_to_pay:
                    messages.error(request, "Du hast zu wenig AP / Magie")
                    return redirect(request.build_absolute_uri())

                # pay AP
                ap_diff = min(char.ap, ap_to_pay)
                ap_to_pay -= ap_diff
                char.ap -= ap_diff
                char.save(update_fields=["ap"])

                # pay MA
                ap_diff = min(rel_ma.aktuellerWert_temp, ap_to_pay)
                ap_to_pay -= ap_diff
                rel_ma.aktuellerWert_temp -= ap_diff

                ap_diff = min(rel_ma.aktuellerWert, ap_to_pay)
                ap_to_pay -= ap_diff
                rel_ma.aktuellerWert -= ap_diff
                rel_ma.save(update_fields=["aktuellerWert", "aktuellerWert_temp"])


            # receive
            rels = []
            for rel in rel_zauber:
                rel.tier = new_tiers[rel.id]
                rels.append(rel)
            RelZauber.objects.bulk_update(rels, fields=["tier"])

            # return
            messages.success(request, "Tiers erfolgreich gespeichert")
            return redirect(request.build_absolute_uri())



        return redirect(request.build_absolute_uri())




class GenericPersonalView(LoginRequiredMixin, VerifiedAccountMixin, HeaderMixin, TemplateView):
    template_name = "levelUp/personal.html"
    topic = "Persönliches"

    def get_character(self) -> Charakter: raise NotImplementedError()


    def get_context_data(self, *args, **kwargs):
        char = self.get_character()

        context = super().get_context_data(*args, **kwargs, form = PersonalForm(instance=char))
        # create or override -> don't cause 'get_context_data() got multiple values for keyword argument 'char''
        context["char"] = char
        return context


    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        char = self.get_character()

        form = PersonalForm(request.POST, instance=char)
        form.full_clean()
        if form.is_valid():
            form.save()

            # Persönlichkeit is not updated automatically if None and stayed on first element in formfield
            RelPersönlichkeit.objects.filter(char=char).delete()
            RelPersönlichkeit.objects.create(char=char, persönlichkeit=form.cleaned_data["persönlichkeit"].first())

            messages.success(request, "Erfolgreich gespeichert")

        return redirect(request.build_absolute_uri())
    

class GenericSpF_wFView(LoginRequiredMixin, OwnCharakterMixin, tables.SingleTableMixin, HeaderMixin, TemplateView):

    def get_character(self) -> Charakter: raise NotImplementedError()


    class Table(GenericTable):

        class Meta:
            attrs = GenericTable.Meta.attrs

        titel = tables.Column(verbose_name="Fertigkeit")
        art = tables.Column(verbose_name="Art")
        attrs = tables.Column(verbose_name="Attribute")
        ferts = tables.Column(verbose_name="Fertigkeit/en")
        wp = tables.Column()

        def render_titel(self, value, record):
            return value
        
        def render_attrs(self, value, record):
            attrs = [record["attr1__titel"], record["attr2__titel"]]
            if "attr3__titel" in record:
                attrs.append(record["attr3__titel"])

            return ", ".join(sorted(attrs))
        
        def render_ferts(self, value, record):
            if record["art"] == "Spezial":
                spezial = Spezialfertigkeit.objects.get(id=record["id"])
                return ", ".join([sp.titel for sp in spezial.ausgleich.all().order_by("titel")])
            
            if record["art"] == "Wissen":
                wissen = Wissensfertigkeit.objects.get(id=record["id"])
                return ", ".join([wi.titel for wi in wissen.fertigkeit.all().order_by("titel")])

        def render_wp(self, value, record):
            value_exists = record["stufe"] is not None
            id = record["id"]

            offset = -5 if record["art"] == "Spezial" else 0


            args = f"min='{offset}'"
            if record["art"] == "Spezial":
                args += f" name='spezial-{id}' class='spezial-input'"
            else:
                args += f" name='wissen-{id}' class='wissen-input'"

            if value_exists:
                args += f" value='{record['stufe']+offset}' required"

            return format_html(f"<input type='number' form='form' {args}>")


    topic = "Spezial- & Wissensf."
    template_name = "levelUp/spF_wF.html"

    table_class = Table
    table_pagination = False


    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs, table = self.Table(self.get_table_data()))
        # create or override -> don't cause 'get_context_data() got multiple values for keyword argument 'char''
        context["char"] = self.get_character()
        return context


    def get_table_data(self):
        """
        Return the table data that should be used to populate the rows.
        """
        # if self.table_data is not None:
        #     return self.table_data
        char = self.get_character()

        spezial = list(
                Spezialfertigkeit.objects.all()\
                    .prefetch_related("attr1", "attr2")\
                    .annotate(
                        art = Value("Spezial"),
                        ferts = Value(0),
                        attrs = Value(0),
                        stufe = Subquery(RelSpezialfertigkeit.objects.filter(char=char, spezialfertigkeit__id=OuterRef("id")).values("stufe")[:1]),
                        wp = Value(0), # replace later
                    )\
                    .values("id", "titel", "art",
                            "attrs", "attr1__titel", "attr2__titel",
                            "ferts", "wp", "stufe"
                    )
            )
        wissen = list(
                Wissensfertigkeit.objects.all()\
                    .prefetch_related("attr1", "attr2", "attr3")\
                    .annotate(
                        art = Value("Wissen"),
                        ferts = Value(0),
                        attrs = Value(0),
                        stufe = Subquery(RelWissensfertigkeit.objects.filter(char=char, wissensfertigkeit__id=OuterRef("id")).values("stufe")[:1]),
                        wp = Value(0),
                    )\
                    .values("id", "titel", "art",
                            "attrs", "attr1__titel", "attr2__titel", "attr3__titel",
                            "ferts", "stufe", "wp"
                    )
            )

        # return objects (ordered by name)
        return sorted(spezial + wissen, key=lambda x: x["titel"])


    def post(self, request: HttpRequest, char: Charakter) -> HttpResponse:

        # collect values
        payment_method = request.POST.get("payment_method")
        spezial_ids = {int(key.replace("spezial-", "")): int(stufe)+5 for key, stufe in request.POST.items() if "spezial-" in key and len(stufe)}
        wissen_ids = {int(key.replace("wissen-", "")): int(stufe) for key, stufe in request.POST.items() if "wissen-" in key and len(stufe)}

        # test them
        if payment_method not in ["points", "sp"]:
            messages.error(request, "Die Zahlungsart für neue Fertigkeiten kenne ich nicht.")

        spezial = RelSpezialfertigkeit.objects\
            .filter(char=char)\
            .aggregate(
                wp = Sum("stufe"),
                fert = Count("*")
            )
        wissen_qs = RelWissensfertigkeit.objects.filter(char=char)
        wissen_wp = sum(wissen_qs.values_list("stufe", flat=True))

        fert_max = (spezial["fert"] or 0) + (wissen_qs.count() or 0) + char.spF_wF
        wp_max = (spezial["wp"] or 0) + (wissen_wp or 0) + char.wp
        fert_max = char.spF_wF if payment_method == "points" else char.sp
        fert_max += (spezial["fert"] or 0) + (wissen_qs.count() or 0)

        # enough to pay for new ferts?
        if len(spezial_ids) + len(wissen_ids) > fert_max:
            messages.error(request, "Du hast zu viele gewählt")

        # enough wp?
        if sum(spezial_ids.values()) + sum(wissen_ids.values()) > wp_max:
            messages.error(request, "Du hast zu viele WP verteilt")

        # permit selling stufe
        faulty_spezial = [rel.spezialfertigkeit.titel for rel in RelSpezialfertigkeit.objects.prefetch_related("spezialfertigkeit").filter(char=char) if rel.spezialfertigkeit.id not in spezial_ids.keys() or spezial_ids[rel.spezialfertigkeit.id] < rel.stufe]
        faulty_wissen = [rel.wissensfertigkeit.titel for rel in RelWissensfertigkeit.objects.prefetch_related("wissensfertigkeit").filter(char=char) if rel.wissensfertigkeit.id not in wissen_ids.keys() or wissen_ids[rel.wissensfertigkeit.id] < rel.stufe]
        if len(faulty_spezial) + len(faulty_wissen) > 0:
            messages.error(request, f"Du kannst keine Stufen (von {', '.join([*faulty_spezial, *faulty_wissen])}) verkaufen")


        # all fine or not?
        if len(messages.get_messages(request)):
            return redirect(request.build_absolute_uri())

        # apply them to db
        if payment_method == "points":
            char.spF_wF = fert_max - len(spezial_ids) - len(wissen_ids)
        else:
            char.sp = fert_max - len(spezial_ids) - len(wissen_ids)
        char.wp = wp_max - sum(spezial_ids.values()) - sum(wissen_ids.values())
        char.save(update_fields=["spF_wF", "sp", "wp"])

        RelSpezialfertigkeit.objects.filter(char=char).delete()
        RelWissensfertigkeit.objects.filter(char=char).delete()
        for sp in Spezialfertigkeit.objects.filter(id__in=spezial_ids):
            RelSpezialfertigkeit.objects.create(char=char, spezialfertigkeit=sp, stufe=spezial_ids[sp.id])
        for wi in Wissensfertigkeit.objects.filter(id__in=wissen_ids):
            RelWissensfertigkeit.objects.create(char=char, wissensfertigkeit=wi, stufe=wissen_ids[wi.id])

        # return response
        messages.success(request, "Erfolgreich gespeichert")
        return redirect(request.build_absolute_uri())


class GenericTalentView(LoginRequiredMixin, OwnCharakterMixin, HeaderMixin, TemplateView):
    
    def get_character(self) -> Charakter: raise NotImplementedError()

    template_name = "levelUp/talent.html"
    topic = "Talent"


    def get_available_talente(self, char):

        own_talent_ids = [rel.talent.id for rel in RelTalent.objects.prefetch_related("talent").filter(char=char)]
        talente = Talent.objects.prefetch_related("bedingung").filter(tp__lte=char.tp).exclude(id__in=own_talent_ids)

        available_talente = []
        for talent in talente:
            bedingung_ids = [b.id for b in talent.bedingung.all()]

            # test bedingungen
            ok = True
            for b_id in bedingung_ids:
                if b_id not in own_talent_ids:
                    ok = False
                    break

            # add if bedingungen all met
            if ok: available_talente.append(talent)

        return available_talente

    def get_context_data(self, *args, **kwargs):
        char = self.get_character()

        context = super().get_context_data(*args, **kwargs,
            own_talente = [rel.talent for rel in RelTalent.objects.filter(char=char)],
            talente = self.get_available_talente(char),
        )
        # create or override -> don't cause 'get_context_data() got multiple values for keyword argument 'char''
        context["char"] = char
        return context


    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        char = self.get_character()

        talent_id = request.POST.get("zauber_id")
        talent = get_object_or_404(Talent, id=talent_id)
        
        # checks
        if not talent in self.get_available_talente(char):
            messages.error(request, f"Das Talent {talent.titel} hast du bereits oder kannst du nicht lernen.")
            return redirect(request.build_absolute_uri())

        # apply
        char.tp -= talent.tp
        char.save(update_fields=["tp"])

        RelTalent.objects.create(char=char, talent=talent)
        return redirect(request.build_absolute_uri())



class GenericWesenkraftView(LoginRequiredMixin, OwnCharakterMixin, HeaderMixin, TemplateView):
    
    def get_character(self) -> Charakter: raise NotImplementedError()

    template_name = "levelUp/wesenkraft.html"
    topic = "Wesenkraft"


    def get_context_data(self, *args, **kwargs):
        char = self.get_character()
        rel_ma = RelAttribut.objects.get(char=char, attribut__titel='MA')

        context = super().get_context_data(*args, **kwargs,
            own_wesenkraft = RelWesenkraft.objects.filter(char=char).order_by("wesenkraft__titel"),
            MA_aktuell = rel_ma.aktuellerWert + rel_ma.aktuellerWert_temp - get_required_aktuellerWert(char, "MA"),
            get_tier_cost_with_sp = get_tier_cost_with_sp(),
        )
        # create or override -> don't cause 'get_context_data() got multiple values for keyword argument 'char''
        context["char"] = char
        return context


    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        char = self.get_character()

        # GATHER DATA
        rel_wesenkraft_ids = [int(id) for id in request.POST.keys() if id.isnumeric()]

        new_tiers = {id: int(request.POST.get(str(id))) for id in rel_wesenkraft_ids}
        rel_wesenkraft = RelWesenkraft.objects.filter(char=char, id__in=rel_wesenkraft_ids)


        # PERFORM CHECKS

        # char already has wesenkraft
        if rel_wesenkraft.count() != len(rel_wesenkraft_ids):
            messages.error(request, "Du wolltest Tier zu Wesenkräften vergeben, die du gar nicht kennst")
            return redirect(request.build_absolute_uri())

        for rel in rel_wesenkraft:
            # not lower than current value
            if rel.tier > new_tiers[rel.id]:
                messages.error(request, "Du kannst Tier nicht wieder verkaufen")
                return redirect(request.build_absolute_uri())
            
            # has to be lower than max_tier
            if rel.tier > char.max_tier_allowed():
                messages.error(request, f"Du kannst Tier nicht über {char.max_tier_allowed()} steigern")
                return redirect(request.build_absolute_uri())

        if request.POST.get("payment_method") == "sp":
            sp = 0
            for rel in rel_wesenkraft:
                new_tier = new_tiers[rel.id]
                existing_tier = rel.tier
                while new_tier > existing_tier:
                    sp += get_tier_cost_with_sp()[new_tier]
                    new_tier -= 1

            # char has enough sp to pay for
            if char.sp < sp:
                messages.error(request, "Du hast zu wenig SP")
                return redirect(request.build_absolute_uri())


            # pay SP
            char.sp -= sp
            char.save(update_fields=["sp"])

        if request.POST.get("payment_method") == "ap":
            rel_ma = get_object_or_404(RelAttribut, char=char, attribut__titel="MA")
            
            ap_available = char.ap + rel_ma.aktuellerWert + rel_ma.aktuellerWert_temp - get_required_aktuellerWert(char, "MA")
            ap_to_pay = sum(new_tiers.values()) - rel_wesenkraft.aggregate(tier_sum=Sum("tier"))["tier_sum"]


            # char has enough AP/MA.aktuellerWert to pay for
            if ap_available < ap_to_pay:
                messages.error(request, "Du hast zu wenig AP / Magie")
                return redirect(request.build_absolute_uri())

            # pay AP
            ap_diff = min(char.ap, ap_to_pay)
            ap_to_pay -= ap_diff
            char.ap -= ap_diff
            char.save(update_fields=["ap"])

            # pay MA
            ap_diff = min(rel_ma.aktuellerWert_temp, ap_to_pay)
            ap_to_pay -= ap_diff
            rel_ma.aktuellerWert_temp -= ap_diff

            ap_diff = min(rel_ma.aktuellerWert, ap_to_pay)
            ap_to_pay -= ap_diff
            rel_ma.aktuellerWert -= ap_diff
            rel_ma.save(update_fields=["aktuellerWert", "aktuellerWert_temp"])


        # receive
        rels = []
        for rel in rel_wesenkraft:
            rel.tier = new_tiers[rel.id]
            rels.append(rel)
        RelWesenkraft.objects.bulk_update(rels, fields=["tier"])

        # return
        messages.success(request, "Tiers erfolgreich gespeichert")
        return redirect(request.build_absolute_uri())


class AffektivitätView(LoginRequiredMixin, OwnCharakterMixin, tables.SingleTableMixin, HeaderMixin, TemplateView):

    def get_character(self) -> Charakter: raise NotImplementedError()


    class Table(GenericTable):

        class Meta:
            attrs = GenericTable.Meta.attrs
            model = Affektivität
            fields = ["name", "wert", "notiz"]

        def render_wert(self, value, record):
            id = record.id
            return format_html(f"<input type='number' form='form' name='wert-{id}' value='{value}' min='-200' max='200' class='input'>")

        def render_notiz(self, value, record):
            id = record.id
            value = record.notizen
            return format_html(f"<textarea form='form' name='notizen-{id}'>{value}</textarea>")


    template_name = "levelUp/affektivität.html"
    topic = "Affektivität"
    model = Affektivität

    table_class = Table
    table_pagination = False

    def get_queryset(self):
        return Affektivität.objects.filter(char=self.get_character())\
            .annotate(notiz=Value(1))   # replace later
    
    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs,
            table = self.Table(self.get_table_data()),
            form = AffektivitätForm()
        )
        # create or override -> don't cause 'get_context_data() got multiple values for keyword argument 'char''
        context["char"] = self.get_character()
        return context

    def post(self, request, *args, **kwargs):
        char = self.get_character()
        method = request.POST.get("method")

        if method == "update":

            # collect values
            wert_ids = {int(key.replace("wert-", "")): int(w) for key, w in request.POST.items() if "wert-" in key and len(w)}
            notizen_ids = {int(key.replace("notizen-", "")): n for key, n in request.POST.items() if "notizen-" in key}

            # test ids
            if len(wert_ids.keys()) != len(notizen_ids.keys()):
                messages.error(request, "Das Format habe ich nicht verstanden. Das waren unterschiedlich viele Werte und Notizen.")
                return redirect(request.build_absolute_uri())

            own_ids = [e.id for e in Affektivität.objects.filter(char=char)]
            for id, wert in wert_ids.items():
                if id not in own_ids or id not in notizen_ids.keys():
                    messages.error(request, "Das Format habe ich nicht verstanden. Die IDs waren durcheinander.")
                    return redirect(request.build_absolute_uri())

            # # apply them to db
            # TODO handle delete

            # update or create
            own_ids = [e.id for e in Affektivität.objects.filter(char=char)]
            for id, wert in wert_ids.items():
                Affektivität.objects.update_or_create(id=id, defaults={"wert": wert, "notizen": notizen_ids[id]})

        if method == "create":
            form = AffektivitätForm(request.POST)
            form.full_clean()
            form.cleaned_data["char"] = char

            # invalid?
            if not form.is_valid():
                messages.error(request, "Nicht valid")
                return redirect(request.build_absolute_uri())

            # add char
            aff = form.save(commit=False)
            aff.char = char
            aff.save()

        # return response
        messages.success(request, "Erfolgreich gespeichert")
        return redirect(request.build_absolute_uri())



class GenericSkilltreeView(LoginRequiredMixin, OwnCharakterMixin, tables.SingleTableMixin, HeaderMixin, TemplateView):

    def get_character(self) -> Charakter: raise NotImplementedError()


    class Table(GenericTable):

        class Meta:
            attrs = GenericTable.Meta.attrs
            model = GfsSkilltreeEntry
            fields = ["chosen", "stufe", "text"]

        chosen = tables.Column(verbose_name="")

        def render_chosen(self, value, record):
            return format_html(f"<input type='checkbox' form='form' name='{record['stufe']}' {'checked disabled' if record['chosen'] else ''}>")

        def render_stufe(self, value, record):
            return format_html(f"<span class='stufe'>{value}</span> (<span class='sp'>{record['sp']}</span> SP)")



    template_name = "levelUp/skilltree.html"
    topic = "Skilltree"
    model = GfsSkilltreeEntry

    table_class = Table
    table_pagination = False

    def get_queryset(self):
        char = self.get_character()

        skilltree = [{"stufe": entry.stufe, "sp": entry.sp, "text": []} for entry in SkilltreeBase.objects.filter(stufe__gt=0).order_by("stufe")]
        entries = GfsSkilltreeEntry.objects.prefetch_related("base")\
            .filter(gfs=char.gfs, base__stufe__gt=0)\
            .order_by("base__stufe")

        # Gfs Skilltree
        for s in entries:

            # offset is -2, because anyone lacks the bonus (with Stufe 0) and starts at Stufe 2
            skilltree[s.base.stufe-2]["text"].append(s.__repr__())

        # list to string
        for s in skilltree: s["text"] = ", ".join(s["text"])

        
        return [{**s, "chosen": s["stufe"] <= char.skilltree_stufe} for s in skilltree]
    
    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs,
            table = self.Table(self.get_table_data())
        )
        # create or override -> don't cause 'get_context_data() got multiple values for keyword argument 'char''
        context["char"] = self.get_character()
        return context

    def post(self, request, *args, **kwargs):
        char = self.get_character()

        skilltree_stufen = set([int(st) for st in request.POST.keys() if st.isnumeric()])
        skilltree = GfsSkilltreeEntry.objects.prefetch_related("base").filter(gfs=char.gfs, base__stufe__gt=char.skilltree_stufe, base__stufe__lte=max(skilltree_stufen))

        # check
        
        # allowed, consecutive stufen?
        for st in skilltree_stufen:
            if not skilltree.filter(base__stufe=st).exists():
                messages.error(request, f"Stufe {st} hast du schon oder gibt es gar nicht")
                return redirect(request.build_absolute_uri())

        # affordable?
        sp_cost = SkilltreeBase.objects.filter(stufe__in=skilltree_stufen).aggregate(sp=Sum("sp"))["sp"]
        if char.sp < sp_cost:
            messages.error(request, f"So viele SP hast du gar nicht")
            return redirect(request.build_absolute_uri())

        # pay
        char.sp -= sp_cost
        char.skilltree_stufe = max(skilltree_stufen)
        char.save(update_fields=["sp", "skilltree_stufe"])

        # collect values
        for s in skilltree: s.apply_to(char)

        # return response
        messages.success(request, "Erfolgreich gespeichert")
        return redirect(request.build_absolute_uri())
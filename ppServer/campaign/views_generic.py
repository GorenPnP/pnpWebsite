import json, re
from math import floor
from typing import Any, Dict

from django.db.models import F, Subquery, OuterRef, Q, Count, Sum, Value, Window, Func, Exists
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http.request import HttpRequest
from django.http.response import HttpResponse, JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic.base import TemplateView
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.utils.html import format_html

import django_tables2 as tables
from django_tables2.columns import TemplateColumn

from ppServer.mixins import VerifiedAccountMixin

from base.abstract_views import DynamicTableView, DynamicTablesView, GenericTable
from character.enums import würfelart_enum
from character.models import *
from create.forms import PersonalForm
from shop.models import Zauber

from .mixins import OwnCharakterMixin
from .models import *


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

        aktuell_ap = TemplateColumn(template_name="create/_number_input.html", extra_context={"add_field": "aktuell", "max_field": "aktuell_limit", "base_name": BASE_AKTUELL, "base_class": BASE_AKTUELL, "dataset_id": "dataset_id"})
        max_ap = TemplateColumn(template_name="create/_number_input.html", extra_context={"add_field": "max","max_field": None, "base_name": BASE_MAX, "base_class": BASE_MAX, "dataset_id": "dataset_id"})

        def render_attribut__titel(self, value, record):
            return f"{value} ({record.attribut.beschreibung})"

        def render_result(self, value, record):
            curr = (record.aktuell or 0) + (record.aktuell_ap or 0)
            max = (record.max or 0) + (record.max_ap or 0)
            return f"{curr} / {max}"


    topic = "Attribute"
    template_name = "create/ap.html"
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

        fp = TemplateColumn(template_name="create/_number_input.html", extra_context={"add_field": "fp_bonus", "max_field": "fp_limit", "base_name": "fp", "base_class": "fp", "dataset_id": "id"})
        fg = TemplateColumn(template_name="create/_number_input.html", extra_context={"add_field": "fg_bonus", "max_field": "fp_limit", "base_name": "fg", "base_class": "fg", "dataset_id": "attr_dataset_id"})

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

        fp = TemplateColumn(template_name="create/_number_input.html", extra_context={"add_field": "fp_bonus", "max_field": "fp_limit", "base_name": "fp", "base_class": "fp", "dataset_id": "id"})

        def render_attribute(self, value, record):
            # like SCH + IN (1)
            return format_html(f"{record.fertigkeit.attr1.titel} + {record.fertigkeit.attr2.titel} (<span class='attr_sum'>{record.attr_sum}</span>)")

        def render_pool(self, value, record):
            return record.attr_sum + record.fp + record.fp_bonus


    topic = "Fertigkeiten"
    template_name = "create/fert.html"
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


class GenericVorteilView(LoginRequiredMixin, OwnCharakterMixin, TemplateView):
    template_name = "campaign/hub_teil.html"
    topic = "Vorteile"

    def get_character(self) -> Charakter: raise NotImplementedError()


    def get_app_index(self):
        return self.app_index

    def get_app_index_url(self):
        return reverse(self.app_index_url)

    def get_topic(self):
        return self.topic 


    def get_context_data(self, *args, **kwargs) -> Dict[str, Any]:
        char = self.get_character()
        situations = ["i", "e"] if char.in_erstellung else ["i", "n"]
        rels = RelVorteil.objects.filter(char=char)

        teils = list(Vorteil.objects\
                .filter(wann_wählbar__in=situations)\
                .prefetch_related("relvorteil_set")\
                .annotate(
                    has_rel=Exists(rels.filter(teil__id=OuterRef("id")))
                )\
                .order_by("-has_rel", "titel")
                .values("id", "titel", "beschreibung", "has_rel", "needs_ip", "needs_attribut", "needs_fertigkeit", "needs_engelsroboter", "needs_notiz", "ip", "min_ip", "max_ip", "is_sellable", "max_amount")
        )
        for teil in teils:
            teil["rel"] = rels.filter(teil__id=teil["id"])

        return {
            "topic": self.get_topic(),
            "app_index": self.get_app_index(),
            "app_index_url": self.get_app_index_url(),
            
            "char": char,
            "object_list": teils,
            "attribute": Attribut.objects.all(),
            "fertigkeiten": Fertigkeit.objects.all(),
            "engelsroboter": Engelsroboter.objects.all()
        }

    def post(self, request, *args, **kwargs):

        changes = {key:value for (key,value) in request.POST.items() if value}
        char = self.get_character()
        ip = 0

        ####### no updates of existing RelVorteil possible #########

        # handle deletions
        deletions = [int(re.search(r'\d+$', key).group(0)) for key in changes.keys() if "delete" in key]
        qs_deletions = RelVorteil.objects.filter(id__in=deletions, char=char)
        ip += sum([rel.ip if rel.teil.needs_ip else rel.teil.ip for rel in qs_deletions.prefetch_related("teil")])
        qs_deletions.delete()


        # handle additions
        additions = [int(re.search(r'\d+$', key).group(0)) for key in changes.keys() if "add" in key]
        changes = {key:value for (key,value) in changes.items() if "delete" not in key and "add" not in key}

        for teil_id in additions:
            fields = {(k.replace(f"-{teil_id}", '')): v for (k, v) in changes.items() if f"-{teil_id}" in k}
            teil = Vorteil.objects.get(id=teil_id)

            # amount
            if teil.max_amount and teil.max_amount <= teil.relvorteil_set.filter(char=char).count():
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
            RelVorteil.objects.create(teil=teil, char=char, **fields)
            ip -= teil.ip if not teil.needs_ip else fields["ip"]


        # apply ip
        char.ip += ip
        char.save()

        return redirect(request.build_absolute_uri())


class GenericZauberView(LoginRequiredMixin, OwnCharakterMixin, DynamicTableView):
    
    def get_character(self) -> Charakter: raise NotImplementedError()


    class Table(GenericTable):

        class Meta:
            model = Zauber
            fields = ["gewählt", "name", "ab_stufe", "beschreibung", "weiteres"]
            attrs = GenericTable.Meta.attrs

        def render_gewählt(self, value, record):
            return format_html(f"<input type='checkbox' form='form' class='zauber-input' name='zauber-{record.id}' {'checked' if value else ''}>")

        def render_beschreibung(self, value, record):
            def func(matchobj):
                return "<b>" + matchobj.group(1) + "</b>" + matchobj.group(2)

            value = re.sub('([Tt]ier [0XVI]+)(:)', func, value).replace("\n", "<br>")

            return format_html(f"<div class='scroll-y'>{value}</div>")
        
        def render_weiteres(self, value, record):
            value = \
                f"<b>Schaden</b>: {record.schaden or '-'}<br>" +\
                f"<b>Astralschaden</b>: {record.astralschaden}<br>" +\
                f"<b>Manaverbrauch</b>: {record.manaverbrauch}<br>" +\
                f"<b>Kategorie</b>: {record.get_kategorie_display()}"
            return format_html(f"<div class='scroll-y'>{value}</div>")

    topic = "Zauber"
    template_name = "create/zauber.html"
    model = Zauber

    table_class = Table
    table_pagination = False


    def get_queryset(self):
        char = self.get_character()
        
        max_stufe = max([int(k) for k in char.zauberplätze.keys()])

        return Zauber.objects\
            .filter(frei_editierbar=False, ab_stufe__lte=max_stufe)\
            .order_by("ab_stufe")\
            .annotate(
                gewählt = Exists(Subquery(RelZauber.objects.filter(char=char, item__id=OuterRef("id")))),
                weiteres = Value(1)     # replace later
            )

    def get_context_data(self, *args, **kwargs):
        char = self.get_character()
        rel_ma = RelAttribut.objects.get(char=char, attribut__titel='MA')

        context = super().get_context_data(*args, **kwargs,
                                           
            char = char,
            max_tier_allowed = min(1 + floor(char.ep_stufe_in_progress / 4), 7),
            existing_zauber = RelZauber.objects.filter(char=char, will_create=False).order_by("item__name"),
            new_zauber = RelZauber.objects.filter(char=char, will_create=True).order_by("item__name"),
            
            zauber = Zauber.objects\
                .filter(frei_editierbar=False, ab_stufe__lte=max([int(e) for e in char.zauberplätze.keys()]))\
                .exclude(id__in=char.zauber.values("id")),

            MA_aktuell = rel_ma.aktuellerWert + rel_ma.aktuellerWert_temp,
        )

        # free zauber slots
        zauber_available = sum(char.zauberplätze.values())
        zauber_spent = context["new_zauber"].count() # +\
        for rel in RelZauber.objects.filter(char=char):
            zauber_spent += len([r for r in rel.tier_notes.values() if r == "slot"])

        context["free_slots"] = zauber_available - zauber_spent

        return context


    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        char = self.get_character()

        # collect values
        zauber_ids = set([int(key.replace("zauber-", "")) for key in request.POST.keys() if "zauber-" in key])

        # test them
        zauber_max = RelZauber.objects\
            .filter(char=char)\
            .aggregate( spent = Count("*") )["spent"] + sum(char.zauberplätze.values())

        if len(zauber_ids) > zauber_max:
            messages.error(request, "Du hast zu viele Zauber gewählt")

        # all fine or not?
        if len(messages.get_messages(request)):
            return redirect(request.build_absolute_uri())

        # # apply them to db
        # char.zauber = zauber_max - len(zauber_ids)
        # char.save(update_fields=["zauber"])

        RelZauber.objects.filter(char=char).delete()
        for zauber in Zauber.objects.filter(id__in=zauber_ids):
            RelZauber.objects.create(char=char, item=zauber)

        # return response
        messages.success(request, "Erfolgreich gespeichert")
        return redirect(request.build_absolute_uri())




class GenericPersonalView(LoginRequiredMixin, VerifiedAccountMixin, TemplateView):
    template_name = "create/personal.html"
    topic = "Persönliches"

    def get_character(self) -> Charakter: raise NotImplementedError()


    def get_app_index(self):
        return self.app_index

    def get_app_index_url(self):
        return reverse(self.app_index_url)

    def get_topic(self):
        return self.topic 

    def get_context_data(self, *args, **kwargs):
        char = self.get_character()

        return {
            "topic": self.get_topic(),
            "app_index": self.get_app_index(),
            "app_index_url": self.get_app_index_url(),
            "form": PersonalForm(instance=char),
            "char": char
        }


    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        form = PersonalForm(request.POST, instance=self.get_character())
        form.full_clean()
        if form.is_valid():
            form.save()

            messages.success(request, "Erfolgreich gespeichert")

        return redirect(request.build_absolute_uri())
    

class GenericSpF_wFView(LoginRequiredMixin, OwnCharakterMixin, tables.SingleTableMixin, TemplateView):

    def get_character(self) -> Charakter: raise NotImplementedError()


    def get_app_index(self):
        return self.app_index

    def get_app_index_url(self):
        return reverse(self.app_index_url)

    def get_topic(self):
        return self.topic 


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
            value = record["stufe"] or 0
            id = record["id"]

            if record["art"] == "Spezial":
                return format_html(f"<input type='number' form='form' name='spezial-{id}' class='spezial-input' min=0 value='{value}'>")

            if record["art"] == "Wissen":
                dice = ["---", "W4", "W6", "W8", "W10", "W12", "W20", "W100"]
                options = "".join([f"<option value='{ stufe }' {'selected' if stufe == value else ''}>{ d }</option>" for stufe, d in enumerate(dice)])
                return format_html(f"<select form='form' name='wissen-{id}' class='wissen-input'>{options}</select>")


    topic = "Spezial- & Wissensf."
    template_name = "create/spF_wF.html"

    table_class = Table
    table_pagination = False


    def get_context_data(self, *args, **kwargs):
        return {
            "topic": self.get_topic(),
            "app_index": self.get_app_index(),
            "app_index_url": self.get_app_index_url(),
            "char": self.get_character()
        }
    
    def get_table_data(self):
        """
        Return the table data that should be used to populate the rows.
        """
        # if self.table_data is not None:
        #     return self.table_data
        char = self.get_character()

        objects = \
            list(
                Spezialfertigkeit.objects.all()\
                    .prefetch_related("attr1", "attr2")\
                    .annotate(
                        art = Value("Spezial"),
                        ferts = Value(0),
                        attrs = Value(0),
                        wp = Value(0),
                        stufe = Subquery(RelSpezialfertigkeit.objects.filter(char=char, spezialfertigkeit__id=OuterRef("id")).values("stufe")[:1]),
                    )\
                    .values("id", "titel", "art" ,
                            "attrs", "attr1__titel", "attr2__titel",
                            "ferts", "wp", "stufe"
                    )
            ) +\
            list(
                Wissensfertigkeit.objects.all()\
                    .prefetch_related("attr1", "attr2", "attr3")\
                    .annotate(
                        art = Value("Wissen"),
                        ferts = Value(0),
                        attrs = Value(0),
                        wp = Value(0),
                        stufe = Subquery(RelWissensfertigkeit.objects.filter(char=char, wissensfertigkeit__id=OuterRef("id")).values("stufe")[:1]),
                    )\
                    .values("id", "titel", "art",
                            "attrs", "attr1__titel", "attr2__titel", "attr3__titel",
                            "ferts" , "wp", "stufe"
                    )
            )

        # return objects (ordered by name)
        return sorted(objects, key=lambda x: x["titel"])


    def post(self, request: HttpRequest, char: Charakter) -> HttpResponse:

        # collect values
        spezial_ids = {int(key.replace("spezial-", "")): int(stufe) for key, stufe in request.POST.items() if "spezial-" in key and int(stufe)}
        wissen_ids = {int(key.replace("wissen-", "")): int(stufe) for key, stufe in request.POST.items() if "wissen-" in key and int(stufe)}

        # test them
        spezial = RelSpezialfertigkeit.objects\
            .filter(char=char)\
            .aggregate(
                wp = Sum("stufe"),
                fert = Count("*")
            )
        wissen = RelWissensfertigkeit.objects\
            .filter(char=char)\
            .aggregate(
                wp = Sum("stufe"),
                fert = Count("*")
            )
        
        fert_max = (spezial["fert"] or 0) + (wissen["fert"] or 0) + char.spF_wF
        wp_max = (spezial["wp"] or 0) + (wissen["wp"] or 0) + char.wp

        if len(spezial_ids) + len(wissen_ids) > fert_max:
            messages.error(request, "Du hast zu viele gewählt")

        if sum(spezial_ids.values()) + sum(wissen_ids.values()) > wp_max:
            messages.error(request, "Du hast zu viele WP verteilt")

        # all fine or not?
        if len(messages.get_messages(request)):
            return redirect(request.build_absolute_uri())

        # apply them to db
        char.spF_wF = fert_max - len(spezial_ids) - len(wissen_ids)
        char.wp = wp_max - sum(spezial_ids.values()) - sum(wissen_ids.values())
        char.save(update_fields=["spF_wF", "wp"])

        RelSpezialfertigkeit.objects.filter(char=char).delete()
        RelWissensfertigkeit.objects.filter(char=char).delete()
        for sp in Spezialfertigkeit.objects.filter(id__in=spezial_ids):
            RelSpezialfertigkeit.objects.create(char=char, spezialfertigkeit=sp, stufe=spezial_ids[sp.id])
        for wi in Wissensfertigkeit.objects.filter(id__in=wissen_ids):
            RelWissensfertigkeit.objects.create(char=char, wissensfertigkeit=wi, stufe=wissen_ids[wi.id])

        # return response
        messages.success(request, "Erfolgreich gespeichert")
        return redirect(request.build_absolute_uri())
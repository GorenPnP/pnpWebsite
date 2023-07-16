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
from character.enums import würfelart_enum
from character.models import *
from shop.models import Zauber

from .forms import PersonalForm
from .mixins import OwnCharakterMixin

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


class GenericTeilView(LoginRequiredMixin, OwnCharakterMixin, TemplateView):
    template_name = "levelUp/teil/teil.html"

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
        rels = self.RelModel.objects.filter(char=char)
        rel_set_name = f"{self.RelModel._meta.model_name}_set"

        # TODO: let sellable sell, but not buy new if in campaign
        # | (Q(is_sellable=True) & Q(relteil_char=char)))\
        teils = list(self.Model.objects\
                .filter(Q(wann_wählbar__in=situations))\
                .prefetch_related(rel_set_name)\
                .annotate(
                    has_rel=Exists(rels.filter(teil__id=OuterRef("id")))
                )\
                .order_by("-has_rel", "titel")
                .values("id", "titel", "beschreibung", "has_rel", "needs_ip", "needs_attribut", "needs_fertigkeit", "needs_engelsroboter", "needs_notiz", "ip", "min_ip", "max_ip", "is_sellable", "max_amount")
        )
        for teil in teils:
            teil["rel"] = rels.filter(teil__id=teil["id"])

        context = super().get_context_data(*args, **kwargs,
            topic = self.get_topic(),
            app_index = self.get_app_index(),
            app_index_url = self.get_app_index_url(),

            is_vorteil = self.is_vorteil,
            object_list = teils,

            attribute = Attribut.objects.all(),
            fertigkeiten = Fertigkeit.objects.all(),
            engelsroboter = Engelsroboter.objects.all()
        )
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
    template_name = "levelUp/zauber.html"
    model = Zauber

    table_class = Table
    table_pagination = False

    def get_tier_cost_with_sp(self):
        return {
            1: 1,
            2: 1,
            3: 1,
            4: 2,
            5: 2,
            6: 2,
            7: 3
        }


    def get_queryset(self):
        char = self.get_character()
        
        max_stufe = max([int(k) for k in char.zauberplätze.keys()], default=-1)

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
        max_stufe = max([int(k) for k in char.zauberplätze.keys()], default=-1)
        zauber = Zauber.objects\
                .filter(frei_editierbar=False, ab_stufe__lte=max_stufe)\
                .exclude(id__in=char.zauber.values("id"))\
                .values("id", "name")
        
        for z in zauber:
            z["geld"] = min([f.getPrice() for f in FirmaZauber.objects.filter(item__id=z["id"])])

        return super().get_context_data(*args, **kwargs,
                                           
            char = char,
            own_zauber = RelZauber.objects.filter(char=char).order_by("item__name"),
            zauber = zauber,

            MA_aktuell = rel_ma.aktuellerWert + rel_ma.aktuellerWert_temp - get_required_aktuellerWert(char, "MA"),
            free_slots = sum(char.zauberplätze.values()),
            get_tier_cost_with_sp = self.get_tier_cost_with_sp(),
        )


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
                        sp += self.get_tier_cost_with_sp()[new_tier]
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




class GenericPersonalView(LoginRequiredMixin, VerifiedAccountMixin, TemplateView):
    template_name = "levelUp/personal.html"
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

        context = super().get_context_data(*args, **kwargs,
            topic = self.get_topic(),
            app_index = self.get_app_index(),
            app_index_url = self.get_app_index_url(),
            form = PersonalForm(instance=char),
        )
        context["char"] = char
        return context


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
            value = record["stufe"]
            id = record["id"]

            if record["art"] == "Spezial":
                args = "min='-5'"
                if record["stufe"] is not None:
                    args = f"min='{value-5}' value='{value-5}' required"

                return format_html(f"<input type='number' form='form' name='spezial-{id}' class='spezial-input' {args}>")

            if record["art"] == "Wissen":
                dice = ["---", "W4", "W6", "W8", "W10", "W12", "W20", "W100"]
                options = "".join([f"<option value='{ index-1 if index else '' }' {'selected' if value is not None and index-1 == value else ''}>{ d }</option>" for index, d in enumerate(dice) if value is None or index > value])
                return format_html(f"<select form='form' name='wissen-{id}' class='wissen-input'>{options}</select>")


    topic = "Spezial- & Wissensf."
    template_name = "levelUp/spF_wF.html"

    table_class = Table
    table_pagination = False


    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs,
            topic = self.get_topic(),
            app_index = self.get_app_index(),
            app_index_url = self.get_app_index_url(),
            table = self.Table(self.get_table_data())
        )
        context["char"] = self.get_character()
        return context
    

    def würfel2_to_stufe(self, würfel2) -> int:
        w_stufen = [w[0] for w in würfelart_enum]
        return w_stufen.index(würfel2)

    def stufe_to_würfel2(self, stufe) -> int:
        return würfelart_enum[stufe][0]


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
                        wp = Value(0),
                        stufe = Subquery(RelSpezialfertigkeit.objects.filter(char=char, spezialfertigkeit__id=OuterRef("id")).values("stufe")[:1]),
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
                        wp = Value(0),
                        würfel2 = Subquery(RelWissensfertigkeit.objects.filter(char=char, wissensfertigkeit__id=OuterRef("id")).values("würfel2")[:1]),
                    )\
                    .values("id", "titel", "art",
                            "attrs", "attr1__titel", "attr2__titel", "attr3__titel",
                            "ferts", "wp", "würfel2"
                    )
            )
        # transform würfel2 to stufe
        wissen = [{**w, "stufe": self.würfel2_to_stufe(w["würfel2"]) if w["würfel2"] else None} for w in wissen]

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
        wissen_wp = sum([self.würfel2_to_stufe(relw.würfel2) for relw in wissen_qs])

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
        faulty_wissen = [rel.wissensfertigkeit.titel for rel in RelWissensfertigkeit.objects.prefetch_related("wissensfertigkeit").filter(char=char) if rel.wissensfertigkeit.id not in wissen_ids.keys() or wissen_ids[rel.wissensfertigkeit.id] < self.würfel2_to_stufe(rel.würfel2)]
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
            RelWissensfertigkeit.objects.create(char=char, wissensfertigkeit=wi, würfel2=self.stufe_to_würfel2(wissen_ids[wi.id]))

        # return response
        messages.success(request, "Erfolgreich gespeichert")
        return redirect(request.build_absolute_uri())
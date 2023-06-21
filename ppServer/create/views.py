import json, re

from django.db.models import F, Subquery, OuterRef, Q, Count, Sum, Value, Window, Func, Exists
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
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
from shop.models import Zauber

from .decorators import *
from .forms import EndForm
from .models import *

class GfsWahlfilterView(LoginRequiredMixin, VerifiedAccountMixin, DynamicTableView):

    model = GfsCharacterization
    topic = "Gfs Wahlfilter"
    template_name = "create/gfs_characterization.html"

    filterset_fields = ["gfs__difficulty", "state", "social", "magical", "can_punch", "can_shoot", "gets_pricy_skills", "can_fly", "attitude"]
    table_fields = ["gfs__titel", "gfs__beschreibung"]

    app_index = "Erstellung"
    app_index_url = "create:gfs"


class LandingPageView(LoginRequiredMixin, VerifiedAccountMixin, TemplateView):

    @method_decorator(cp_done)
    @method_decorator(provide_new_char)
    @method_decorator(gfs_done)
    @method_decorator(prio_done)
    def get(self, request: HttpRequest, new_char: NewCharakter) -> HttpResponse:

        # rows
        rows = []
        rows.append({"done": is_ap_done(request, new_char=new_char), "link": reverse("create:ap"), "text": "<b>Attribute</b> verteilen", "werte": "{} AP".format(new_char.ap), "id": "attr"})
        rows.append({"done": is_ferts_done(request, new_char=new_char), "link": reverse("create:fert"), "text": "<b>Fertigkeiten</b> verteilen",
                     "werte": "{} FP<br>{} FG".format(new_char.fp, new_char.fg), "id": "fert"})

        if not new_char.larp:
            rows.append({"done": is_zauber_done(request, new_char=new_char), "link": reverse("create:zauber"), "text": "<b>Zauber</b> aussuchen", "werte": "{} offen".format(new_char.zauber)})
            rows.append({"done": is_spF_wF_done(request, new_char=new_char), "link": reverse("create:spF_wF"), "text": "<b>Spezial- und Wissensfertigkeiten</b> wählen", "werte": "{} offen<br>{} WP".format(new_char.spF_wF, new_char.wp)})
        rows.append({"done": is_teil_done(request, new_char=new_char), "link": reverse("create:vor_nachteil"), "text": "<b>Vor- und Nachteile</b> nehmen", "werte": "{} IP".format(new_char.ip)})

        # submit-btn disabled state
        done_completely =\
            is_ap_done(request, new_char=new_char) and\
            is_ferts_done(request, new_char=new_char) and\
            is_zauber_done(request, new_char=new_char) and\
            is_spF_wF_done(request, new_char=new_char) and\
            is_teil_done(request, new_char=new_char) and\
            NewCharakterPersönlichkeit.objects.filter(char=new_char).exists()

        # persönlichkeiten
        rel_pers = Persönlichkeit.objects.filter(id__in=Subquery(
            NewCharakterPersönlichkeit.objects
                .prefetch_related("char", "persönlichkeit")
                .filter(char=new_char)
                .values("persönlichkeit__id")
            ))
        persönlichkeit_row = {
                "done": rel_pers.exists(),
                "link": reverse("wiki:persönlichkeiten"),
                "werte": Persönlichkeit.objects.annotate(
                    selected=Count("id", distinct=True, filter=Q(id__in=rel_pers)
                ))
            }

        # infos
        infos = [
            "<strong>Deine Gfs/Klasse</strong> kannst du dir <a href='{}' target='_blank'>hier</a> nochmal angucken.".format(reverse("wiki:stufenplan", args=[new_char.gfs.id])),
            "Aussehen und v.A. rollenspielwichtige Aspekte wie Religion, Beruf werden später festgelegt.",
            "Im <strong>Shop</strong> kann später eingekauft werden, für Neugierige geht's zum Stöbern <a href='{}' target='_blank'>hier</a> entlang.".format(reverse("shop:index")),
        ]

        # assemble context & render
        context = {
            "topic": "Erstellungshub",
            "rows": rows,
            "done": done_completely,
            "persönlichkeit_row": persönlichkeit_row,
            "infos": infos,
            "app_index": "Erstellung",
            "app_index_url": reverse("create:gfs"),
        }
        return render(request, "create/landing_page.html", context=context)

    @method_decorator(provide_new_char)
    def post(self, request: HttpRequest, new_char: NewCharakter) -> HttpResponse:

        try:
            p_ids = [int(p_id) for p_id in json.loads(request.body.decode("utf-8"))['p_ids']]
        except:
            return JsonResponse({"message": "Keine Persönlichkeit angekommen"}, status=418)

        toggle_check = NewCharakterPersönlichkeit.objects.filter(char=new_char).count() == 0     # if persönlichkeit chosen, tick that box!


        # persönlichkeit hinzufügen
        NewCharakterPersönlichkeit.objects.filter(char=new_char).delete()
        for persönlichkeit in Persönlichkeit.objects.filter(id__in=p_ids):
            NewCharakterPersönlichkeit.objects.create(char=new_char, persönlichkeit=persönlichkeit)

        # done
        return JsonResponse({"toggle_check": toggle_check})


class GfsFormView(LoginRequiredMixin, VerifiedAccountMixin, TemplateView):

    def get(self, request: HttpRequest) -> HttpResponse:

        username = request.user.username
        old_scetches = Gfs.objects\
            .prefetch_related("newcharakter_set__eigentümer", "charakter_set__eigentümer")\
            .filter(Q(newcharakter__eigentümer__name=username) | Q(charakter__eigentümer__name=username, charakter__in_erstellung=True))\

        context = {
            "gfs": Gfs.objects.all(),
            "old_scetches": old_scetches,
            "topic": "Charakter erstellen",
            "app_index": "Erstellung",
            "app_index_url": reverse("create:gfs"),
        }

        return render(request, "create/gfs.html", context)

    def post(self, request: HttpRequest) -> HttpResponse:
        try:
            gfs_id = json.loads(request.body.decode("utf-8"))["gfs_id"]
            larp = json.loads(request.body.decode("utf-8"))["larp"]
        except:
            return JsonResponse({"message": "Keine Gfs angekommen"}, status=418)

        spieler = get_object_or_404(Spieler, name=request.user.username)
        gfs = get_object_or_404(Gfs, id=gfs_id)

        # alle Charaktere in_erstellung löschen
        Charakter.objects.filter(eigentümer=spieler, in_erstellung=True).delete()

        # jeder nur ein NewCharakter zurzeit
        NewCharakter.objects.filter(eigentümer=spieler).delete()

        new_char = NewCharakter.objects.create(eigentümer=spieler, gfs=gfs, larp=larp)

        # set default vals
        if larp:
            new_char.ap = 100
            new_char.fp = 20
            new_char.fg = 2
            new_char.geld = 5000
            new_char.sp = 0
            new_char.ip = 0
            new_char.zauber = 0
            new_char.save(update_fields=["ap", "fp", "fg", "geld", "sp", "ip", "zauber"])


        return JsonResponse({"url": reverse("create:prio")})


class PriotableFormView(LoginRequiredMixin, VerifiedAccountMixin, TemplateView):

    # number of WP per spF & wF chosen
    WP_FACTOR = 4

    def get_entries(self):
        return Priotable.objects.all().values_list("priority", "ip", "ap", "sp", "konzentration", "fp", "fg", "zauber", "drachmen", "spF_wF")


    @method_decorator(cp_done)
    @method_decorator(provide_new_char)
    @method_decorator(gfs_done)
    @method_decorator(prio_not_done)
    def get(self, request: HttpRequest, new_char: NewCharakter) -> HttpResponse:
        entries = self.get_entries()
        
        # get ap cost for gfs
        ap_cost = new_char.gfs.ap

        # # get MA maximum
        # max_MA = max_MA = GfsAttribut.objects.get(gfs=new_char.gfs, attribut__titel="MA").maxWert

        # # mundan => keine Zauber wählbar (nur 0 Zauber in prio F)
        # if max_MA == 0:
        #     for k in range(entries.count()):
        #         entries[k][7] = entries[k][7] and None  # produces 0 | None

        notes = [
            "IP = für Vor- und Nachteile",
            "AP = Aufwerten eines Attributs",
            "SP = für alles Mögliche, vor Allem um nicht zu sterben",
            "Konz. = Konzentration, um Proben besser zu würfeln als sonst",
            "FP = Fertigkeitspunkte",
            "FG = Fertigkeitsgruppen",
        ]

        context = {
            "topic": "Prioritätentabelle",
            'table': entries,
            'notizen': notes,
            "ap_cost": ap_cost,
            "gfs": new_char.gfs,
            "app_index": "Erstellung",
            "app_index_url": reverse("create:gfs"),
        }
        return render(request, "create/prio.html", context)

    @method_decorator(cp_done)
    @method_decorator(provide_new_char)
    @method_decorator(gfs_done)
    @method_decorator(prio_not_done)
    def post(self, request: HttpRequest, new_char: NewCharakter) -> HttpResponse:
        entries = self.get_entries()

        # collect data
        num_entries = entries.count()
        if new_char is None:
            return JsonResponse({"url": reverse("create:gfs")}, status=300)

        fields = {}
        try:
            for k, v in json.loads(request.body.decode("utf-8")).items(): fields[k] = int(v)
        except:
            return JsonResponse({'message': 'Falsche Auswahl (Format)'}, status=418)

        if len(fields.values()) != num_entries:
            return JsonResponse({"message": "Falsche Auswahl (Anzahl Felder)"}, status=418)

        for val in fields.values():
            if val < 0 or val >= num_entries:
                return JsonResponse({"message": "Falsche Auswahl (Inhalt Felder)"}, status=418)

        # start logic
        ap = new_char.gfs.ap * -1
        for category in fields.keys():
            row = fields[category]
            col = int(category) + 1

            # row: [priority, IP, AP, (SP, konzentration), (FP, FG), Zauber, Drachmen]
            if col == 1:
                new_char.ip = entries[row][col]
            elif col == 2:
                ap = entries[row][col]

            elif col == 3:
                new_char.sp = entries[row][col]
                new_char.konzentration = entries[row][col + 1]
            elif col == 4:
                new_char.fp = entries[row][col + 1]
                new_char.fg = entries[row][col + 2]
            elif col == 5:
                new_char.zauber = entries[row][col + 2]
            else:
                new_char.geld = entries[row][col + 2]
                new_char.spF_wF = entries[row][col + 3]
                new_char.wp = entries[row][col + 3] * self.WP_FACTOR

        ap -= new_char.gfs.ap
        if ap < 0:
            return JsonResponse({"message": "Zu wenig AP für Gfs"}, status=418)

        new_char.ap = ap
        new_char.save(update_fields=["ip", "sp", "konzentration", "fp", "fg", "zauber", "geld", "spF_wF", "wp", "ap"])

        return JsonResponse({"url": reverse("create:landing_page")})


class ApFormView(LoginRequiredMixin, VerifiedAccountMixin, DynamicTableView):

    BASE_AKTUELL = "aktuell"
    BASE_MAX = "max"
    class Table(GenericTable):
        BASE_AKTUELL = "aktuell"
        BASE_MAX = "max"

        class Meta:
            model = NewCharakterAttribut
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
    model = NewCharakterAttribut

    table_class = Table

    app_index = "Erstellung"
    app_index_url = "create:gfs"

    def get_queryset(self):
        new_char, error = get_own_NewCharakter(self.request)
        if not new_char or error:
            raise "Charakter konnte nicht gefunden werden"

        return NewCharakterAttribut.objects.prefetch_related("char").filter(char=new_char).annotate(
            aktuell = F("aktuellerWert") + F("aktuellerWert_bonus"),
            aktuell_ap = F("aktuellerWert_ap"),
            aktuell_limit = F("maxWert") + F("maxWert_bonus") + F("maxWert_ap") - F("aktuellerWert") - F("aktuellerWert_bonus"),
            max = F("maxWert") + F("maxWert_bonus"),
            max_ap = F("maxWert_ap"),
            result=Value(1), # override later
            dataset_id=F("attribut__id")
        )

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context["new_char"] = context["object_list"][0].char
        return context

    @method_decorator(cp_done)
    @method_decorator(provide_new_char)
    @method_decorator(gfs_done)
    @method_decorator(prio_done)
    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        return super().get(request, *args, **kwargs)

    @method_decorator(cp_done)
    @method_decorator(provide_new_char)
    @method_decorator(gfs_done)
    @method_decorator(prio_done)
    def post(self, request: HttpRequest, new_char: NewCharakter) -> HttpResponse:

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
            )["spent"] + new_char.ap

        if ap_spent > ap_max:
            messages.error(request, "Du hast zu wenig AP")

        # all fine or not?
        if len(messages.get_messages(request)):
            return redirect(request.build_absolute_uri())

        # apply them to db
        new_char.ap = ap_max - ap_spent
        new_char.save(update_fields=["ap"])

        relattrs = []
        for relattr in NewCharakterAttribut.objects.prefetch_related("attribut", "char").filter(char=new_char):
            relattr.aktuellerWert_ap = ap[relattr.attribut.id]["aktuell"]
            relattr.maxWert_ap = ap[relattr.attribut.id]["max"]
            relattrs.append(relattr)
        NewCharakterAttribut.objects.bulk_update(relattrs, ["aktuellerWert_ap", "maxWert_ap"])

        # return response
        messages.success(request, "Erfolgreich gespeichert")
        return redirect(request.build_absolute_uri())


class FertigkeitFormView(LoginRequiredMixin, VerifiedAccountMixin, DynamicTablesView):

    class Table1(GenericTable):

        class Meta:
            model = NewCharakterFertigkeit
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
            model = NewCharakterFertigkeit
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
    model = NewCharakterFertigkeit

    tables = [Table1, TableElse]
    table_pagination = False

    app_index = "Erstellung"
    app_index_url = "create:gfs"

    def get_queryset(self):
        new_char, error = get_own_NewCharakter(self.request)
        if not new_char or error:
            raise "Charakter konnte nicht gefunden werden"

        # will be a subquery for all (1 or 2) NewCharakterAttributes related to NewCharakterFertigkeit by fertigkeit.attr1 & fertigkeit.attr2
        attr_qs = NewCharakterAttribut.objects.prefetch_related("char")\
            .filter(char=new_char)\
            .filter(Q(attribut=OuterRef("fertigkeit__attr1")) | Q(attribut=OuterRef("fertigkeit__attr2")))\
            .annotate(
            aktuell = F("aktuellerWert") + F("aktuellerWert_bonus") + F("aktuellerWert_ap")
        )

        return NewCharakterFertigkeit.objects\
            .prefetch_related("char", "fertigkeit", "fertigkeit__attr1", "fertigkeit__attr2")\
            .filter(char=new_char)\
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
        context["new_char"] = context["object_list"][0].char
        return context


    @method_decorator(cp_done)
    @method_decorator(provide_new_char)
    @method_decorator(gfs_done)
    @method_decorator(prio_done)
    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        return super().get(request, *args, **kwargs)


    @method_decorator(cp_done)
    @method_decorator(provide_new_char)
    @method_decorator(gfs_done)
    @method_decorator(prio_done)
    def post(self, request: HttpRequest, new_char: NewCharakter) -> HttpResponse:

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
        for relattr in NewCharakterAttribut.objects.filter(char=new_char):
            attr = relattr.attribut

            # get & sanitize
            rel_fg = int(request.POST.getlist(f"fg-{attr.id}")[0])  # getting array of 3 identical because html contains 3 with similar "name" attrs
            if rel_fg + relfert.fg_bonus > relattr.aktuellerWert + relattr.aktuellerWert_bonus + relattr.aktuellerWert_ap:
                messages.error(request, f"Bei {attr} sind die FG höher als erlaubt")

            # save in temporal datastructure
            fg[attr.id] = rel_fg

        #### test them ####
        # fp
        fp_max = self.get_queryset().aggregate(
                spent = Sum("fp")
            )["spent"] + new_char.fp

        if sum(fp.values()) > fp_max:
            messages.error(request, "Du hast zu wenig FP")

        # fg
        fg_max = NewCharakterAttribut.objects.filter(char=new_char).aggregate(
                spent = Sum("fg")
            )["spent"] + new_char.fg

        if sum(fg.values()) > fg_max:
            messages.error(request, "Du hast zu wenig FG")

        #### all fine or not? ####
        if len(messages.get_messages(request)):
            return redirect(request.build_absolute_uri())

        #### apply them to db ###
        new_char.fp = fp_max - sum(fp.values())
        new_char.fg = fg_max - sum(fg.values())
        new_char.save(update_fields=["fp", "fg"])

        relattrs = []
        for relattr in NewCharakterAttribut.objects.prefetch_related("attribut", "char").filter(char=new_char):
            relattr.fg = fg[relattr.attribut.id]
            relattrs.append(relattr)
        NewCharakterAttribut.objects.bulk_update(relattrs, ["fg"])
        
        relferts = []
        for relfert in NewCharakterFertigkeit.objects.prefetch_related("fertigkeit", "char").filter(char=new_char):
            relfert.fp = fp[relfert.fertigkeit.id]
            relferts.append(relfert)
        NewCharakterFertigkeit.objects.bulk_update(relferts, ["fp"])

        # return response
        messages.success(request, "Erfolgreich gespeichert")
        return redirect(request.build_absolute_uri())


class ZauberFormView(LoginRequiredMixin, VerifiedAccountMixin, DynamicTableView):

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

    app_index = "Erstellung"
    app_index_url = "create:gfs"

    def get_queryset(self):
        new_char, error = get_own_NewCharakter(self.request)
        if not new_char or error:
            raise "Charakter konnte nicht gefunden werden"

        return Zauber.objects\
            .filter(frei_editierbar=False)\
            .order_by("ab_stufe")\
            .annotate(
                gewählt = Exists(Subquery(NewCharakterZauber.objects.filter(char=new_char, item__id=OuterRef("id")))),
                weiteres = Value(1)     # replace later
            )

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context["new_char"] = self.new_char
        return context

    @method_decorator(cp_done)
    @method_decorator(provide_new_char)
    @method_decorator(gfs_done)
    @method_decorator(prio_done)
    def get(self, request: HttpRequest, new_char: NewCharakter, *args, **kwargs) -> HttpResponse:
        self.new_char = new_char
        return super().get(request, *args, **kwargs, new_char=new_char)

    @method_decorator(cp_done)
    @method_decorator(provide_new_char)
    @method_decorator(gfs_done)
    @method_decorator(prio_done)
    def post(self, request: HttpRequest, new_char: NewCharakter) -> HttpResponse:

        # collect values
        zauber_ids = set([int(key.replace("zauber-", "")) for key in request.POST.keys() if "zauber-" in key])

        # test them
        zauber_max = NewCharakterZauber.objects\
            .filter(char=new_char)\
            .aggregate( spent = Count("*") )["spent"] + new_char.zauber

        if len(zauber_ids) > zauber_max:
            messages.error(request, "Du hast zu viele Zauber gewählt")

        # all fine or not?
        if len(messages.get_messages(request)):
            return redirect(request.build_absolute_uri())

        # apply them to db
        new_char.zauber = zauber_max - len(zauber_ids)
        new_char.save(update_fields=["zauber"])

        NewCharakterZauber.objects.filter(char=new_char).delete()
        for zauber in Zauber.objects.filter(id__in=zauber_ids):
            NewCharakterZauber.objects.create(char=new_char, item=zauber)

        # return response
        messages.success(request, "Erfolgreich gespeichert")
        return redirect(request.build_absolute_uri())


class SpF_wFFormView(LoginRequiredMixin, VerifiedAccountMixin, tables.SingleTableMixin, TemplateView):

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
        context = super().get_context_data(*args, **kwargs)
        context["new_char"] = self.new_char
        context["app_index"] = "Erstellung"
        context["app_index_url"] = reverse("create:gfs")
        return context
    
    def get_table_data(self):
        """
        Return the table data that should be used to populate the rows.
        """
        # if self.table_data is not None:
        #     return self.table_data

        objects = \
            list(
                Spezialfertigkeit.objects.all()\
                    .prefetch_related("attr1", "attr2")\
                    .annotate(
                        art = Value("Spezial"),
                        ferts = Value(0),
                        attrs = Value(0),
                        wp = Value(0),
                        stufe = Subquery(NewCharakterSpezialfertigkeit.objects.filter(char=self.new_char, spezialfertigkeit__id=OuterRef("id")).values("stufe")[:1]),
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
                        stufe = Subquery(NewCharakterWissensfertigkeit.objects.filter(char=self.new_char, wissensfertigkeit__id=OuterRef("id")).values("stufe")[:1]),
                    )\
                    .values("id", "titel", "art",
                            "attrs", "attr1__titel", "attr2__titel", "attr3__titel",
                            "ferts" , "wp", "stufe"
                    )
            )

        # return objects (ordered by name)
        return sorted(objects, key=lambda x: x["titel"])


    @method_decorator(cp_done)
    @method_decorator(provide_new_char)
    @method_decorator(gfs_done)
    @method_decorator(prio_done)
    def get(self, request: HttpRequest, new_char: NewCharakter, *args, **kwargs) -> HttpResponse:
        self.new_char = new_char
        return super().get(request, *args, **kwargs, new_char=new_char)

    @method_decorator(cp_done)
    @method_decorator(provide_new_char)
    @method_decorator(gfs_done)
    @method_decorator(prio_done)
    def post(self, request: HttpRequest, new_char: NewCharakter) -> HttpResponse:

        # collect values
        spezial_ids = {int(key.replace("spezial-", "")): int(stufe) for key, stufe in request.POST.items() if "spezial-" in key and int(stufe)}
        wissen_ids = {int(key.replace("wissen-", "")): int(stufe) for key, stufe in request.POST.items() if "wissen-" in key and int(stufe)}

        # test them
        spezial = NewCharakterSpezialfertigkeit.objects\
            .filter(char=new_char)\
            .aggregate(
                wp = Sum("stufe"),
                fert = Count("*")
            )
        wissen = NewCharakterWissensfertigkeit.objects\
            .filter(char=new_char)\
            .aggregate(
                wp = Sum("stufe"),
                fert = Count("*")
            )
        
        fert_max = (spezial["fert"] or 0) + (wissen["fert"] or 0) + new_char.spF_wF
        wp_max = (spezial["wp"] or 0) + (wissen["wp"] or 0) + new_char.wp

        if len(spezial_ids) + len(wissen_ids) > fert_max:
            messages.error(request, "Du hast zu viele gewählt")

        if sum(spezial_ids.values()) + sum(wissen_ids.values()) > wp_max:
            messages.error(request, "Du hast zu viele WP verteilt")

        # all fine or not?
        if len(messages.get_messages(request)):
            return redirect(request.build_absolute_uri())

        # apply them to db
        new_char.spF_wF = fert_max - len(spezial_ids) - len(wissen_ids)
        new_char.wp = wp_max - sum(spezial_ids.values()) - sum(wissen_ids.values())
        new_char.save(update_fields=["spF_wF", "wp"])

        NewCharakterSpezialfertigkeit.objects.filter(char=new_char).delete()
        NewCharakterWissensfertigkeit.objects.filter(char=new_char).delete()
        for sp in Spezialfertigkeit.objects.filter(id__in=spezial_ids):
            NewCharakterSpezialfertigkeit.objects.create(char=new_char, spezialfertigkeit=sp, stufe=spezial_ids[sp.id])
        for wi in Wissensfertigkeit.objects.filter(id__in=wissen_ids):
            NewCharakterWissensfertigkeit.objects.create(char=new_char, wissensfertigkeit=wi, stufe=wissen_ids[wi.id])

        # return response
        messages.success(request, "Erfolgreich gespeichert")
        return redirect(request.build_absolute_uri())


class TeilFormView(LoginRequiredMixin, VerifiedAccountMixin, DynamicTablesView):

    class VorteilTable(GenericTable):
        class Meta:
            model = Vorteil
            fields = ["anzahl", "titel", "ip", "beschreibung", "notizen"]
            attrs = dict(**GenericTable.Meta.attrs, **{"id": "vorteil-table"})
        
        anzahl = TemplateColumn(template_name="create/_number_input.html", extra_context={"add_field": None, "max_field": "max_amount", "base_name": "vorteil-anzahl", "base_class": "anzahl", "dataset_id": "id"})
        notizen = TemplateColumn(template_name="create/_text_input.html", extra_context={"maxlength": 200, "base_name": "vorteil-notizen", "base_class": "notizen", "dataset_id": "id"})

        def render_ip(self, value, record):
            return format_html(f"<span class='ip' data-id={record.id}>{value}</span>")

    class NachteilTable(VorteilTable):
        class Meta:
            model = Nachteil
            fields = ["anzahl", "titel", "ip", "beschreibung", "notizen"]
            attrs = dict(**GenericTable.Meta.attrs, **{"id": "nachteil-table"})

        anzahl = TemplateColumn(template_name="create/_number_input.html", extra_context={"add_field": None, "max_field": "max_amount", "base_name": "nachteil-anzahl", "base_class": "anzahl", "dataset_id": "id"})
        notizen = TemplateColumn(template_name="create/_text_input.html", extra_context={"maxlength": 200, "base_name": "nachteil-notizen", "base_class": "notizen", "dataset_id": "id"})


    model = Vorteil
    topic = "Vor- und Nachteile"
    template_name = "create/vor_nachteil.html"

    tables = [VorteilTable, NachteilTable]
    table_pagination = False

    app_index = "Erstellung"
    app_index_url = "create:gfs"


    def get_tables_data(self):
        return [
            self.get_vorteil_queryset(),
            self.get_nachteil_queryset(),
        ]
    
    def get_vorteil_queryset(self):
        rel_qs = NewCharakterVorteil.objects.prefetch_related("teil", "char").filter(teil__id=OuterRef("id"), char=self.new_char)

        return Vorteil.objects\
            .filter(wann_wählbar__in=["i", "e"])\
            .annotate(
                notizen=Subquery(rel_qs.values("notizen")[:1]),
                anzahl=Subquery(rel_qs.values("anzahl")[:1])
            )

    def get_nachteil_queryset(self):
        rel_qs = NewCharakterNachteil.objects.prefetch_related("teil", "char").filter(teil__id=OuterRef("id"), char=self.new_char)

        return Nachteil.objects\
            .filter(wann_wählbar__in=["i", "e"])\
            .annotate(
                notizen=Subquery(rel_qs.values("notizen")[:1]),
                anzahl=Subquery(rel_qs.values("anzahl")[:1])
            )


    @method_decorator(cp_done)
    @method_decorator(provide_new_char)
    @method_decorator(gfs_done)
    @method_decorator(prio_done)
    def get(self, request: HttpRequest, new_char: NewCharakter, *args, **kwargs) -> HttpResponse:
        self.new_char = new_char
        return super().get(request, *args, **kwargs)


    @method_decorator(cp_done)
    @method_decorator(provide_new_char)
    @method_decorator(gfs_done)
    @method_decorator(prio_done)
    def post(self, request: HttpRequest, new_char: NewCharakter) -> HttpResponse:
        self.new_char = new_char

        # #### collect values ####
        # vorteile
        vorteile = {}
        for teil in self.get_vorteil_queryset():

            # get & sanitize
            anzahl = int(request.POST.get(f"vorteil-anzahl-{teil.id}"))
            if teil.max_amount is not None and anzahl > teil.max_amount:
                messages.error(request, f"{teil.titel} kannst du nur {teil.max_amount}x haben")

            # save in temporal datastructure
            if anzahl != 0:
                vorteile[teil.id] = {"anzahl": anzahl, "notizen": request.POST.get(f"vorteil-notizen-{teil.id}"), "ip": anzahl * teil.ip}
        
        # nachteile
        nachteile = {}
        for teil in self.get_nachteil_queryset():

            # get & sanitize
            anzahl = int(request.POST.get(f"nachteil-anzahl-{teil.id}"))
            if teil.max_amount is not None and anzahl > teil.max_amount:
                messages.error(request, f"{teil.titel} kannst du nur {teil.max_amount}x haben")

            # save in temporal datastructure
            if anzahl != 0:
                nachteile[teil.id] = {"anzahl": anzahl, "notizen": request.POST.get(f"nachteil-notizen-{teil.id}"), "ip": anzahl * teil.ip}

        #### test them ####
        max_ip = new_char.ip +\
            self.get_vorteil_queryset().annotate(ip_total = F("anzahl") * F("ip")).aggregate(ip=Sum("ip_total"))["ip"] -\
            self.get_nachteil_queryset().annotate(ip_total = F("anzahl") * F("ip")).aggregate(ip=Sum("ip_total"))["ip"]

        ip_spent = sum([teil["ip"] for teil in vorteile.values()])
        ip_gained = sum([teil["ip"] for teil in nachteile.values()])

        ip = max_ip + ip_gained - ip_spent
        if ip < 0:
            messages.error(request, "Du hast zu wenig IP")

        #### all fine or not? ####
        if len(messages.get_messages(request)):
            return redirect(request.build_absolute_uri())

        # #### apply them to db ###
        new_char.ip = ip
        new_char.save(update_fields=["ip"])
        
        NewCharakterVorteil.objects.filter(char=new_char).delete()
        for teil in Vorteil.objects.filter(id__in=vorteile.keys()):
            NewCharakterVorteil.objects.create(
                char=new_char, teil=teil,
                anzahl=vorteile[teil.id]["anzahl"],
                notizen=vorteile[teil.id]["notizen"],
            )
        NewCharakterNachteil.objects.filter(char=new_char).delete()
        for teil in Nachteil.objects.filter(id__in=nachteile.keys()):
            NewCharakterNachteil.objects.create(
                char=new_char, teil=teil,
                anzahl=nachteile[teil.id]["anzahl"],
                notizen=nachteile[teil.id]["notizen"],
            )

        # return response
        messages.success(request, "Erfolgreich gespeichert")
        return redirect(request.build_absolute_uri())


class EndFormView(LoginRequiredMixin, VerifiedAccountMixin, TemplateView):

    template_name = "create/cp.html"
    topic = "Abschluss"

    def transfer_to_Charakter(self, new_char):
        
        # transition from NewCharakter to Charakter
        c = Charakter.objects.create(sp=new_char.sp, konzentration=new_char.konzentration, geld=new_char.geld,
                                    eigentümer=new_char.eigentümer, manifest=new_char.gfs.startmanifest, gfs=new_char.gfs,
                                    larp=new_char.larp, wesenschaden_andere_gestalt=new_char.gfs.wesenschaden_andere_gestalt,
                                    wesenschaden_waff_kampf=new_char.gfs.wesenschaden_waff_kampf,
                                    ep_system=new_char.ep_system, ip=new_char.ip, profession=new_char.profession,
                                    HPplus=new_char.HPplus, HPplus_fix=new_char.HPplus_fix)

        # there is a signal that adds attr & fert to a character on every save. delete these again
        RelAttribut.objects.filter(char=c).delete()

        for rel in NewCharakterAttribut.objects.filter(char=new_char):
            RelAttribut.objects.create(char=c, attribut=rel.attribut, aktuellerWert=rel.ges_aktuell(),
                                        aktuellerWert_bonus=rel.aktuellerWert_bonus, maxWert_bonus=rel.maxWert_bonus,
                                        maxWert=rel.ges_max(), fg=rel.ges_fg())

        # there is a signal that adds attr & fert to a character on every save. delete these again
        RelFertigkeit.objects.filter(char=c).delete()

        for rel in NewCharakterFertigkeit.objects.filter(char=new_char):
            RelFertigkeit.objects.create(
                char=c, fertigkeit=rel.fertigkeit, fp=rel.fp, fp_bonus=rel.fp_bonus)


        for rel in NewCharakterPersönlichkeit.objects.filter(char=new_char):
            RelPersönlichkeit.objects.create(char=c, persönlichkeit=rel.persönlichkeit)

        for rel in NewCharakterVorteil.objects.filter(char=new_char):
            RelVorteil.objects.create(char=c, teil=rel.teil, notizen=rel.notizen, anzahl=rel.anzahl)

        for rel in NewCharakterNachteil.objects.filter(char=new_char):
            RelNachteil.objects.create(char=c, teil=rel.teil, notizen=rel.notizen, anzahl=rel.anzahl)

        for rel in NewCharakterTalent.objects.filter(char=new_char):
            RelTalent.objects.create(char=c, talent=rel.talent)

        for rel in NewCharakterSpezialfertigkeit.objects.filter(char=new_char):
            RelSpezialfertigkeit.objects.create(char=c, spezialfertigkeit=rel.spezialfertigkeit, stufe=rel.stufe)

        for rel in NewCharakterWissensfertigkeit.objects.filter(char=new_char):
            RelWissensfertigkeit.objects.create(char=c, wissensfertigkeit=rel.wissensfertigkeit, würfel2=würfelart_enum[rel.stufe-1][0])

        for rel in GfsWesenkraft.objects.filter(gfs=new_char.gfs):
            RelWesenkraft.objects.create(char=c, wesenkraft=rel.wesenkraft)

        for rel in NewCharakterZauber.objects.filter(char=new_char):
            RelZauber.objects.create(char=c, item=rel.item, anz=1)

        new_char.delete()

        if c.larp:
            c.beruf = get_object_or_404(Beruf, titel="Schüler")
            c.save(update_fields=["beruf"])

        return c


    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        new_char, error = get_own_NewCharakter(request)
        if error:
            return JsonResponse({"message": "Charakter konnte nicht gefunden werden"}, status=418)

        if new_char:
            c = self.transfer_to_Charakter(new_char)

        # new_char already deleted
        else:
            c = Charakter.objects.filter(eigentümer__name=request.user.username, in_erstellung=True).first()
            if c is None: return redirect("create:gfs")

        return render(request, self.template_name, {
            "form": EndForm(instance=c),
            "topic": self.topic,
            "larp": c.larp,
            "app_index": "Erstellung",
            "app_index_url": reverse("create:gfs"),
        })


    @method_decorator(cp_not_done)
    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:

        character = get_object_or_404(Charakter, in_erstellung=True, eigentümer__name=request.user.username)

        if request.user.username != character.eigentümer.name:
            messages.error("Du hast keine Erlaubnis die Charaktererstellung eines fremden Charakters zu beenden")
            return redirect(request.build_absolute_uri())

        form = EndForm(request.POST, instance=character)
        form.full_clean()
        if form.is_valid():
            char = form.save(commit=False)
            char.in_erstellung = False
            char.save()

            return redirect("character:index")

        return render(request, self.template_name, {"form": form, "topic": self.topic})

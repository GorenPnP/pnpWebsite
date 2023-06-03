import re
from typing import Any, Dict

from django.contrib import messages
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from django.db.models import OuterRef, Value, F, Sum, Exists
from django.shortcuts import get_object_or_404, redirect, reverse
from django.views.generic import DetailView

from django_tables2.columns import TemplateColumn

from base.abstract_views import GenericTable
from character.models import Charakter, Vorteil, RelVorteil, Spieler, RelAttribut, Attribut, Fertigkeit
from log.create_log import logAuswertung
from ppServer.mixins import SpielleiterOnlyMixin
from shop.models import Engelsroboter

from .forms import AuswertungForm


class AuswertungView(LoginRequiredMixin, SpielleiterOnlyMixin, DetailView):
    model = Charakter

    template_name = "campaign/auswertung.html"

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs, form=AuswertungForm())
        context["topic"] = 'Auswertung für ' + context["object"].name

        return context

    def post(self, request, *args, **kwargs):
        form = AuswertungForm(request.POST)
        form.full_clean()
        if form.is_valid():
            object = self.get_object()
            fields = {**form.cleaned_data}
            story = fields["story"]
            del fields["story"]

            for k, v in fields.items():
                old_value = getattr(object, k)
                setattr(object, k, old_value + v)

            object.save(update_fields=fields)
            logAuswertung(object.eigentümer, object, story, fields)

            # check ep for new stufe
            object.init_stufenhub()

            return redirect("character:show", object.id)

        return redirect(request.build_absolute_uri())


# TODO: add AccessMixin: only access id something distributable. Only let spieler & spielleiter access
class HubView(DetailView):
    model = Charakter

    template_name = "campaign/hub.html"

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        char = context["object"]

        base_qs = []
        if char.gfs:
            base_qs = char.gfs.gfsstufenplan_set\
                .prefetch_related("basis")\
                .filter(basis__stufe__gt=char.ep_stufe, basis__stufe__lte=char.ep_stufe_in_progress)
            
            stufenbelohnung = []
            for stufe in base_qs:
                stufen_str = []
                if stufe.basis.ap: stufen_str.append(f"<b class='badge rounded-pill' style='background-color: var(--bs-pink)'>+{stufe.basis.ap} AP</b>")
                if stufe.basis.fp: stufen_str.append(f"<b class='badge rounded-pill' style='background-color: var(--bs-indigo)'>+{stufe.basis.fp} FP</b>")
                if stufe.basis.fg: stufen_str.append(f"<b class='badge rounded-pill' style='background-color: var(--bs-blue)'>+{stufe.basis.fg} FG</b>")
                if stufe.basis.tp: stufen_str.append(f"+{stufe.basis.tp} TP")
                if stufe.zauber: stufen_str.append(f"+{stufe.zauber} Zauberslots")
                if stufe.special_ability: stufen_str.append(f"Gfs-Fähigkeit {stufe.special_ability}")

                stufenbelohnung.append(f"Stufe {stufe.basis.stufe} gibt: " + ", ".join(stufen_str))

        return {
            **context,
            "topic": "Verteilungshub",
            'char': char,
            "vorteile": RelVorteil.objects.filter(char=char, will_create=True),
            "stufenbelohnung": stufenbelohnung,
            "app_index": char.name,
            "app_index_url": reverse("character:show", args=[char.id]),
        }


class HubAttributeView(DetailView):

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


    model = RelAttribut
    template_name = "campaign/hub_attribute.html"
    
    topic="AP",
    app_index="Verteilungshub",

    table_class = Table


    def get_queryset(self):

        return RelAttribut.objects.prefetch_related("char").filter(char=self.get_object()).annotate(
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
        context["char"] = context["object_list"][0].char
        context["app_index_url"]=reverse("campaign:hub", args=[self.get_object().id]),
        return context


    def post(self, request, char: Charakter):

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
            relattr.aktuellerWert_ap = ap[relattr.attribut.id]["aktuell"]
            relattr.maxWert_ap = ap[relattr.attribut.id]["max"]
            relattrs.append(relattr)
        RelAttribut.objects.bulk_update(relattrs, ["aktuellerWert_ap", "maxWert_ap"])

        # return response
        messages.success(request, "Erfolgreich gespeichert")
        return redirect(request.build_absolute_uri())


class HubFertigkeitenView(DetailView):
    model = Charakter
    template_name = "campaign/hub_fertigkeiten.html"

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        return super().get_context_data(
            **kwargs,
            topic="FP/FG",
            app_index="Verteilungshub",
            app_index_url=reverse("campaign:hub", args=[self.get_object().id]),
        )


class HubVorteileView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = Charakter
    template_name = "campaign/hub_teil.html"

    # let only owner and spielleiter access
    def test_func(self):
        if self.request.user.groups.filter(name="spielleiter").exists(): return True

        char = self.get_object()
        if not hasattr(char, "eigentümer"): return False

        spieler = get_object_or_404(Spieler, name=self.request.user.username)
        return char.eigentümer == spieler


    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        char = self.get_object()
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

        return super().get_context_data(
            **kwargs,
            topic="Vorteile",
            app_index="Verteilungshub",
            app_index_url=reverse("campaign:hub", args=[char.id]),
            
            object_list=teils,
            attribute=Attribut.objects.all(),
            fertigkeiten=Fertigkeit.objects.all(),
            engelsroboter=Engelsroboter.objects.all()
        )

    def post(self, request, *args, **kwargs):

        changes = {key:value for (key,value) in request.POST.items() if value}
        char = self.get_object()
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

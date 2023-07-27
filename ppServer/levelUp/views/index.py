from typing import Any, Dict

from django.db.models import Q
from django.contrib import messages
from django.http import HttpRequest, HttpResponse
from django.shortcuts import reverse, redirect
from django.views.generic import DetailView
from django.utils.decorators import method_decorator

from character.models import Charakter, RelVorteil, RelNachteil, RelAttribut, RelGfsAbility
from levelUp.decorators import is_done_entirely, pending_areas, is_ap_done, is_ferts_done, is_personal_done, is_spF_wF_done, is_zauber_done
from levelUp.views import *
from log.create_log import render_number

from ..decorators import is_erstellung_done
from ..mixins import LevelUpMixin


@method_decorator([is_erstellung_done], name="dispatch")
class IndexView(LevelUpMixin, DetailView):
    model = Charakter

    template_name = "levelUp/index.html"

    
    def _get_url(self, viewname: str, char: Charakter=None):
        if char is None: char = self.get_character()

        return reverse(f"levelUp:{viewname}", args=[char.id])
    
    def build_table(self, char: Charakter):
        # PREPARATIONS
        rel_ma = RelAttribut.objects.get(char=char, attribut__titel='MA')
        MA_aktuell = rel_ma.aktuellerWert + rel_ma.aktuellerWert_temp - get_required_aktuellerWert(char, 'MA')
        wesenkr_werte = "<br>".join([
            f"{char.sp} SP",
            f"{char.ap} AP / {MA_aktuell} MA"
        ])

        if not char.zauberplätze:
            char.zauberplätze = {}
            char.save(update_fields=["zauberplätze"])
        zauber_werte = "<br>".join([
            *[f"{amount} Stufe {stufe} Zauber" for stufe, amount in char.zauberplätze.items()],
            wesenkr_werte
        ])


        rows = []



        # HALF - AUTOMATIC

        # Vorteile
        attr_filter = (Q(teil__needs_attribut=True) & Q(attribut__isnull=True))
        fert_filter = (Q(teil__needs_fertigkeit=True) & Q(fertigkeit__isnull=True))
        robot_filter = (Q(teil__needs_engelsroboter=True) & Q(engelsroboter__isnull=True))
        ip_filter = (Q(teil__needs_ip=True) & (Q(ip__isnull=True) | Q(ip=0)))
        notizen_filter = (Q(teil__needs_notiz=True) & (Q(notizen__isnull=True) | Q(notizen="")))

        relvorteils = RelVorteil.objects.prefetch_related("teil")\
            .filter(char=char)\
            .filter(attr_filter | fert_filter | robot_filter | ip_filter | notizen_filter)

        if relvorteils.count():
            rows.append({"done": False, "link": self._get_url("vorteile", char), "text": "<b>Rückfragen bei Vorteilen</b>", "werte": ", ".join([rel.teil.titel for rel in relvorteils])})


        # Nachteile
        relnachteils = RelNachteil.objects.prefetch_related("teil")\
            .filter(char=char)\
            .filter(attr_filter | fert_filter | robot_filter | ip_filter | notizen_filter)

        if relnachteils.count():
            rows.append({"done": False, "link": self._get_url("nachteile", char), "text": "<b>Rückfragen bei Nachteilen</b>", "werte": ", ".join([rel.teil.titel for rel in relnachteils])})


        # Gfs-Abilities
        relabilities = RelGfsAbility.objects.prefetch_related("ability").filter(Q(char=char) & Q(ability__has_choice=True) & (Q(notizen__isnull=True) | Q(notizen="")))
        if relabilities.count():
            rows.append({"done": False, "link": self._get_url("gfs_ability", char), "text": "<b>Rückfragen bei Gfs-Fähigkeiten</b>", "werte": ", ".join([rel.teil.name for rel in relabilities])})



        # SOMETIMES AVAILABLE

        # Attribute
        if char.ap or char.relattribut_set.filter(Q(aktuellerWert_temp__gt=0) | Q(maxWert_temp__gt=0)).exists():
            rows.append({"done": is_ap_done(char, 1), "link": self._get_url("attribute", char), "text": "<b>Attribute</b>", "werte": f"{char.ap} AP"})
        # Fertigkeiten
        if char.fp or char.fg or char.relattribut_set.filter(fg_temp__gt=0).exists() or char.relfertigkeit_set.filter(fp_temp__gt=0).exists():
            rows.append({"done": is_ferts_done(char), "link": self._get_url("fertigkeiten", char), "text": "<b>Fertigkeiten</b>", "werte": f"{char.fp} FP<br>{char.fg} FG"})



        # ALWAYS AVAILABLE

        # Personal
        rows.append({"done": is_personal_done(char), "link": self._get_url("personal", char), "text": "<b>Persönliches</b>", "werte": "-"})
        # Skilltree
        rows.append({"done": None, "link": self._get_url("skilltree", char), "text": "<b>Skilltree</b>", "werte": f"{char.sp} SP"})
        # Teile
        rows.append({"done": char.ip >= 0, "link": self._get_url("vorteile", char), "text": "<b>Vorteile</b>", "werte": f"{char.ip} IP"})
        rows.append({"done": char.ip >= 0, "link": self._get_url("nachteile", char), "text": "<b>Nachteile</b>", "werte": f"{char.ip} IP"})
        # Zauber
        if char.zauberplätze.keys() or char.zauber.exists():
            rows.append({"done": is_zauber_done(char), "link": self._get_url("zauber", char), "text": "<b>Zauber</b>", "werte": zauber_werte})
        # Spezis & Wissis
        if char.spF_wF or char.wp or char.spezialfertigkeiten.exists() or char.wissensfertigkeiten.exists():
            rows.append({"done": is_spF_wF_done(char), "link": self._get_url("spF_wF", char), "text": "<b>Spezial- und Wissensfertigkeiten</b>", "werte": f"{char.spF_wF} offen<br>{char.wp} WP<br>{char.sp} SP"})
        # Talente
        if char.tp or char.talente.exists():
            rows.append({"done": True if char.tp == 0 else None, "link": self._get_url("talent", char), "text": "<b>Talente</b>", "werte": f"{char.tp} TP"})
        # Wesenkräfte
        if char.wesenkräfte.exists():
            rows.append({"done": None, "link": self._get_url("wesenkraft", char), "text": "<b>Wesenkräfte</b>", "werte": wesenkr_werte})
        # Shop
        rows.append({"done": None, "link": reverse("shop:index"), "text": "<b>Shop</b>", "werte": f"{render_number(char.geld)} Drachmen"})
        # Affektivität
        rows.append({"done": None, "link": self._get_url("affektivität", char), "text": "<b>Affektivität</b>", "werte": "-"})


        return rows


    def get_context_data(self, *args, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(*args, **kwargs)
        char = context["char"]

        base_qs = []
        stufenbelohnung = []
        if char.gfs:
            base_qs = char.gfs.gfsstufenplan_set\
                .prefetch_related("basis")\
                .filter(basis__stufe__gt=char.ep_stufe, basis__stufe__lte=char.ep_stufe_in_progress)
            
            for stufe in base_qs:
                stufen_str = []
                if stufe.basis.ap: stufen_str.append(f"<b class='badge rounded-pill' style='background-color: var(--bs-pink)'>+{stufe.basis.ap} AP</b>")
                if stufe.basis.fp: stufen_str.append(f"<b class='badge rounded-pill' style='background-color: var(--bs-indigo)'>+{stufe.basis.fp} FP</b>")
                if stufe.basis.fg: stufen_str.append(f"<b class='badge rounded-pill' style='background-color: var(--bs-blue)'>+{stufe.basis.fg} FG</b>")
                if stufe.basis.tp: stufen_str.append(f"+{stufe.basis.tp} TP")
                if stufe.zauber: stufen_str.append(f"+{stufe.zauber} Zauberslots")
                if stufe.ability: stufen_str.append(f"Gfs-Fähigkeit {stufe.ability.name}")

                stufenbelohnung.append(f"Stufe {stufe.basis.stufe} gibt: " + ", ".join(stufen_str))


        notizen = ["Du kannst alle TP sparen"]
        if not char.in_erstellung: notizen.append("Du kannst 1 AP sparen")

        return {
            **context,
            "topic": "Hub",
            "rows": self.build_table(char),
            "is_done": self.request.user.username == char.eigentümer.name and is_done_entirely(char), # is eigentümer & done
            "pending_areas": ", ".join(pending_areas(char)),
            "stufenbelohnung": stufenbelohnung,
            "app_index": char.name,
            "app_index_url": reverse("character:show", args=[char.id]),
            "notizen": notizen
        }


    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        
        # add messages from ep-stufe distribution
        char = self.get_character()
        if "campaign" in char.processing_notes:
            for msg in char.processing_notes["campaign"]:
                messages.error(request, msg)
        
        return super().get(request, *args, **kwargs)


    def post(self, request, *args, **kwargs):
        char = self.get_character()
        if not is_done_entirely(char):
            messages.error(request, "Du hast noch nicht alle nötigen Werte verteilt")
            messages.error(request, "Es fehlt noch: " + ", ".join(pending_areas()))
            return redirect(request.build_absolute_uri())
        
        # not eigentümer
        if self.request.user.username != char.eigentümer.name:
            messages.error(request, "Du bist nichtEigentümer des Charakters und kannst deshalb die Verteilung nicht beenden.")
            return redirect(request.build_absolute_uri())
        
        char = self.get_character()
        char.submit_stufenhub()

        return redirect(reverse("character:show", args=[char.id]))

from functools import cmp_to_key
import re
from typing import Dict, Any

from django.db.models import Q
from django.contrib import messages
from django.shortcuts import redirect
from django.views.generic.base import TemplateView
from django.utils.decorators import method_decorator

from character.models import RelVorteil, RelNachteil, Attribut, Fertigkeit, Nachteil, Vorteil
from shop.models import Engelsroboter

from ..decorators import is_erstellung_done
from ..mixins import LevelUpMixin


def sort_teils(a, b):
    if len(a["rel"]) and not len(b["rel"]): return -1
    if not len(a["rel"]) and len(b["rel"]): return 1

    return -1 if a["titel"] <= b["titel"] else 1


@method_decorator([is_erstellung_done], name="dispatch")
class GenericTeilView(LevelUpMixin, TemplateView):
    template_name = "levelUp/teil/teil.html"


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
            topic = "Vorteile" if self.is_vorteil else "Nachteile",
            is_vorteil = self.is_vorteil,
            object_list = sorted(displayed_teils_dict.values(), key=cmp_to_key(sort_teils)),

            attribute = Attribut.objects.all(),
            fertigkeiten = Fertigkeit.objects.all(),
            engelsroboter = Engelsroboter.objects.all()
        )
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
    RelModel = RelNachteil
    Model = Nachteil
    is_vorteil = False

    def calc_ip_on_creation(self, ip, ip_of_teil) -> int:
        return ip + ip_of_teil
    
    def calc_ip_on_deletion(self, ip, ip_of_teil) -> int:
        return ip - ip_of_teil

class GenericVorteilView(GenericTeilView):
    RelModel = RelVorteil
    Model = Vorteil
    is_vorteil = True

    def calc_ip_on_creation(self, ip, ip_of_teil) -> int:
        return ip - ip_of_teil
    
    def calc_ip_on_deletion(self, ip, ip_of_teil) -> int:
        return ip + ip_of_teil

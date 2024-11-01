from django.db.models import Sum
from django.db.models.functions import Coalesce
from django.shortcuts import get_object_or_404, redirect

from character.models import Charakter, RelVorteil, RelNachteil, RelGfsAbility
from create.decorators import is_prio_done


def is_erstellung_done(view_func, redirect_to="create:gfs"):
    def wrap(request, pk: int, *args, **kwargs):
        char = get_object_or_404(Charakter, pk=pk)
        if not char.in_erstellung or (char.gfs is not None and is_prio_done(char)):
            return view_func(request, *args, **kwargs)
        
        return redirect(redirect_to)
    return wrap

def is_personal_done(char: Charakter):
    return char is not None and char.name is not None and len(char.name) > 0 and char.persönlichkeit

def is_klasse_done(char: Charakter):
    return char is not None and char.ep_stufe_in_progress == char.relklasse_set.aggregate(stufen=Coalesce(Sum("stufe"), 0))["stufen"]

def is_ap_done(char: Charakter, max_ap: int = 0):
    return char is not None and (char.ap is None or char.ap <= max_ap)

def is_ferts_done(char: Charakter):
    return char is not None and not char.fp and not char.fg

def is_zauber_done(char: Charakter):
    return char is not None and len(char.zauberplätze.keys()) == 0

def is_teil_done(char: Charakter):
    return char is not None and char.ip >= 0 and\
        not RelVorteil.objects.filter(char=char, will_create=True).exists() and\
        not RelNachteil.objects.filter(char=char, will_create=True).exists()

def is_spF_wF_done(char: Charakter):
    return char is not None and not char.spF_wF and not char.wp

def is_gfs_ability_done(char=Charakter):
    return char is not None and not RelGfsAbility.objects.prefetch_related("ability").filter(char=char, notizen__isnull=True, ability__has_choice=True).exists()


def is_done_entirely(char: Charakter) -> bool:
    return len(pending_areas(char)) == 0

def pending_areas(char: Charakter) -> list:
        max_ap = 0 if char.in_erstellung else 1

        res = []

        if not is_klasse_done(char): res.append("Klassen")
        if not is_ap_done(char, max_ap): res.append("Attribute")
        if not is_ferts_done(char): res.append("Fertigkeiten")
        if not is_zauber_done(char): res.append("Zauber")
        if not is_personal_done(char): res.append("persönliche Informationen")
        if not is_spF_wF_done(char): res.append("Spezial- und Wissensfertigkeiten")
        if not is_teil_done(char): res.append("Vor- und Nachteile")
        if not is_gfs_ability_done(char): res.append("Gfs-Fähigkeiten")

        return res
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
    return char is not None and char.name and char.persönlichkeit.exists()

def is_ap_done(char: Charakter, max_ap: int = 0):
    return char is not None and char.ap <= max_ap

def is_ferts_done(char: Charakter):
    return char is not None and not char.fp and not char.fg

def is_zauber_done(char: Charakter):
    return char is not None and len(char.zauberplätze.keys()) == 0

def is_teil_done(char: Charakter):
    done = char is not None and char.ip >= 0
    for rel_v in list(RelVorteil.objects.prefetch_related("teil").filter(char=char)) + list(RelNachteil.objects.prefetch_related("teil").filter(char=char)):
        if (rel_v.teil.needs_attribut and not rel_v.attribut) or\
            (rel_v.teil.needs_fertigkeit and not rel_v.fertigkeit) or\
            (rel_v.teil.needs_engelsroboter and not rel_v.engelsroboter) or\
            (rel_v.teil.needs_ip and not rel_v.ip):
                done = False
                break

    return done

def is_spF_wF_done(char: Charakter):
    return char is not None and not char.spF_wF and not char.wp

def is_gfs_ability_done(char=Charakter):
    return char is not None and not RelGfsAbility.objects.prefetch_related("ability").filter(char=char, notizen__isnull=True, ability__has_choice=True).exists()


def is_done_entirely(char: Charakter) -> bool:
    return len(pending_areas(char)) == 0

def pending_areas(char: Charakter) -> list:
        max_ap = 0 if char.in_erstellung else 1

        res = []

        if not is_ap_done(char, max_ap): res.append("Attribute")
        if not is_ferts_done(char): res.append("Fertigkeiten")
        if not is_zauber_done(char): res.append("Zauber")
        if not is_personal_done(char): res.append("persönliche Informationen")
        if not is_spF_wF_done(char): res.append("Spezial- und Wissensfertigkeiten")
        if not is_teil_done(char): res.append("Vor- und Nachteile")
        if not is_gfs_ability_done(char): res.append("Gfs-Fähigkeiten")

        return res
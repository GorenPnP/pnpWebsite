from django.shortcuts import get_object_or_404, redirect, reverse

from character.models import Charakter


def is_prio_done(char: Charakter):
    return char is not None and not (
        char.ap is None or
        char.sp is None or
        char.ip is None or
        char.fp is None or
        char.fg is None or
        char.zauberplätze is None or
        char.geld is None
    )


# decorators

def is_gfs_done(view_func):
    def wrap(request, pk: int, *args, **kwargs):
        char = get_object_or_404(Charakter, pk=pk)
        if char.gfs is not None:
            return view_func(request, pk, *args, **kwargs)
        
        return redirect("create:gfs")
    return wrap


def is_prio_missing(view_func):
    def wrap(request, pk: int, *args, **kwargs):
        char = get_object_or_404(Charakter, pk=pk)
        if char.gfs is None:
            return redirect("create:gfs")

        if is_prio_done(char):
            return redirect(reverse("levelUp:index", args=[char.id]))
        
        return view_func(request, pk, *args, **kwargs)

    return wrap

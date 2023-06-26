from django.http.response import JsonResponse
from django.shortcuts import get_object_or_404, redirect

from character.models import Spieler, Charakter
from shop.models import Zauber

from .models import *


def provide_char(view_func):
    def wrap(request, *args, **kwargs):
        char, error = get_own_charakter(request)
        if error:
            return JsonResponse({"message": "Charakter konnte nicht gefunden werden"}, status=418)

        # print(char)
        return view_func(request, *args, **kwargs, char=char)
    return wrap


def is_done(test, redirect_to="base:index"):
    def decorator(view_func):
        def wrap(request, *args, **kwargs):
            if test(*args, **kwargs, request=request): return view_func(request, *args, **kwargs)

            return redirect(redirect_to)
        return wrap
    return decorator

def is_not_done(test, redirect_to="base:index"):
    def decorator(view_func):
        def wrap(request, *args, **kwargs):
            if not test(*args, **kwargs, request=request): return view_func(request, *args, **kwargs)

            return redirect(redirect_to)
        return wrap
    return decorator



def gfs_done(view_func):
    return is_done(is_gfs_done, "create:gfs")(view_func)

def prio_done(view_func):
    return is_done(is_prio_done, "create:prio")(view_func)


def prio_not_done(view_func):
    return is_not_done(is_prio_done, "create:landing_page")(view_func)


def get_own_charakter(request):

    try:
        spieler = get_object_or_404(Spieler, name=request.user.username)
    except:
        return None, ValueError("Spieler konnte nicht gefunden werden")

    chars = Charakter.objects.filter(eigentümer=spieler, in_erstellung=True)
    if chars.count() > 1:
        return None, ValueError("Es existieren mehrere Charaktere zu diesem Spieler")

    elif chars.count() == 0:
        return None, None
    else:
        return chars.first(), None
    
def is_gfs_done(request, *args, **kwargs):
    done = "char" in kwargs and hasattr(kwargs["char"], "gfs") and kwargs["char"].gfs
    not done and print("GFS not done")
    return done

def is_prio_done(request, *args, **kwargs):
    done = "char" in kwargs and not (
        kwargs["char"].ap is None or
        kwargs["char"].sp is None or
        kwargs["char"].ip is None or
        kwargs["char"].fp is None or
        kwargs["char"].fg is None or
        kwargs["char"].zauberplätze is None or
        kwargs["char"].geld is None
    )
    not done and print("PRIO not done")
    return done

def is_personal_done(*args, **kwargs):
    done = "char" in kwargs and kwargs["char"].name and kwargs["char"].persönlichkeit.exists()
    not done and print("Personal not done")
    return done

def is_ap_done(*args, **kwargs):
    done = "char" in kwargs and kwargs["char"].ap == 0
    not done and print("AP not done")
    return done

def is_ferts_done(*args, **kwargs):
    done = "char" in kwargs and kwargs["char"].fp == 0 and kwargs["char"].fg == 0
    not done and print("FERTS not done")
    return done

def is_zauber_done(*args, **kwargs):
    done = "char" in kwargs and len(kwargs["char"].zauberplätze.keys()) == 0

    not done and print("ZAUBER not done")
    return done

def is_teil_done(*args, **kwargs):
    done = "char" in kwargs and kwargs["char"].ip >= 0
    not done and print("TEIL not done")
    return done

def is_spF_wF_done(*args, **kwargs):
    done = "char" in kwargs and kwargs["char"].spF_wF == 0 and kwargs["char"].wp == 0
    not done and print("spF, wF not done")
    return done

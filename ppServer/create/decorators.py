from django.http.response import JsonResponse
from django.shortcuts import get_object_or_404, redirect

from character.models import Spieler, Charakter

from .models import *


def provide_new_char(view_func):
    def wrap(request, *args, **kwargs):
        new_char, error = get_own_NewCharakter(request)
        if error:
            return JsonResponse({"message": "Charakter konnte nicht gefunden werden"}, status=418)

        # print(new_char)
        return view_func(request, *args, **kwargs, new_char=new_char)
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

def ap_done(view_func):
    return is_done(is_ap_done, "create:ap")(view_func)

def ferts_done(view_func):
    return is_done(is_ferts_done, "create:fert")(view_func)

def zauber_done(view_func):
    return is_done(is_zauber_done, "create:zauber")(view_func)

def teil_done(view_func):
    return is_done(is_teil_done, "create:vor_nachteil")(view_func)

def spF_wF_done(view_func):
    return is_done(is_spF_wF_done, "create:spF_wF")(view_func)

def cp_done(view_func):
    return is_done(is_cp_done, "create:cp")(view_func)


def prio_not_done(view_func):
    return is_not_done(is_prio_done, "create:landing_page")(view_func)

def cp_not_done(view_func):
    return is_not_done(is_cp_done, "create:prio")(view_func)

# def ap_done(view_func):
#     return is_done(is_ap_done, "create:ap")(view_func)

# def ferts_done(view_func):
#     return is_done(is_ferts_done, "create:fert")(view_func)

# def zauber_done(view_func):
#     return is_done(is_zauber_done, "create:zauber")(view_func)

# def teil_done(view_func):
#     return is_done(is_teil_done, "create:vor_nachteil")(view_func)

# def spF_wF_done(view_func):
#     return is_done(is_spF_wF_done, "create:spF_wF")(view_func)

# def cp_done(view_func):
#     return is_done(is_cp_done, "create:cp")(view_func)


def get_own_NewCharakter(request):

    try:
        spieler = get_object_or_404(Spieler, name=request.user.username)
    except:
        return None, ValueError("Spieler konnte nicht gefunden werden")

    chars = NewCharakter.objects.filter(eigentümer=spieler)
    if chars.count() > 1:
        return None, ValueError("Es existieren mehrere Charaktere zu diesem Spieler")

    elif chars.count() == 0:
        return None, None
    else:
        return chars.first(), None
    
def is_gfs_done(request, *args, **kwargs):
    done = "new_char" in kwargs and hasattr(kwargs["new_char"], "gfs") and kwargs["new_char"].gfs
    not done and print("GFS not done")
    return done

def is_prio_done(request, *args, **kwargs):
    done = "new_char" in kwargs and not (
        kwargs["new_char"].ap is None or
        kwargs["new_char"].sp is None or
        kwargs["new_char"].ip is None or
        kwargs["new_char"].fp is None or
        kwargs["new_char"].fg is None or
        kwargs["new_char"].zauber is None or
        kwargs["new_char"].geld is None
    )
    not done and print("PRIO not done")
    return done

def is_ap_done(*args, **kwargs):
    done = "new_char" in kwargs and kwargs["new_char"].ap == 0
    not done and print("AP not done")
    return done

def is_ferts_done(*args, **kwargs):
    done = "new_char" in kwargs and kwargs["new_char"].fp == 0 and kwargs["new_char"].fg == 0
    not done and print("FERTS not done")
    return done

def is_zauber_done(*args, **kwargs):
    done = "new_char" in kwargs and kwargs["new_char"].zauber == 0
    not done and print("ZAUBER not done")
    return done

def is_teil_done(*args, **kwargs):
    done = "new_char" in kwargs and kwargs["new_char"].ip >= 0
    not done and print("TEIL not done")
    return done

def is_spF_wF_done(*args, **kwargs):
    done = "new_char" in kwargs and kwargs["new_char"].spF_wF == 0 and kwargs["new_char"].wp == 0
    not done and print("spF, wF not done")
    return done

def is_cp_done(*args, **kwargs):
    spieler = get_object_or_404(Spieler, name=kwargs["request"].user.username)
    done = NewCharakter.objects.filter(eigentümer=spieler).exists() or not Charakter.objects.filter(eigentümer=spieler, in_erstellung=True).exists()
    not done and print("CP not done")
    return done
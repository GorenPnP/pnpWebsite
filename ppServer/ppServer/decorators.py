from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required


verified_account = login_required


def spielleitung_only(redirect_to="base:index"):
    def decorator(view_func):
        def wrap(request, *args, **kwargs):
            if request.spieler.is_spielleitung:
                return view_func(request, *args, **kwargs)
            else:
                return redirect(redirect_to)
        return wrap
    return decorator


def LARPler_only(redirect_to="base:index"):
    def decorator(view_func):
        def wrap(request, *args, **kwargs):
            if "LARP-ler" in request.spieler.groups:
                return view_func(request, *args, **kwargs)
            else:
                return redirect(redirect_to)
        return wrap
    return decorator


from django.shortcuts import redirect


def TODOperson_only(redirect_to="base:index"):
    def decorator(view_func):
        def wrap(request, *args, **kwargs):
            if "TODO-Kalender" in request.spieler.groups:
                return view_func(request, *args, **kwargs)
            else:
                return redirect(redirect_to)
        return wrap
    return decorator
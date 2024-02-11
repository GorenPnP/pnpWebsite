from django.shortcuts import redirect

def verified_account(view_func):
    def wrap(request, *args, **kwargs):
        if request.spieler.is_verified:
            return view_func(request, *args, **kwargs)
        else:
            return redirect("base:index")
    return wrap


def spielleiter_only(redirect_to="base:index"):
    def decorator(view_func):
        def wrap(request, *args, **kwargs):
            if request.spieler.is_spielleiter:
                return view_func(request, *args, **kwargs)
            else:
                return redirect(redirect_to)
        return wrap
    return decorator

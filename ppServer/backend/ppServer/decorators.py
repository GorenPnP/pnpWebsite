from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required

from character.models import CustomPermission

def _permission_decorator_factory(permissions: list[str], redirect_to: str):
    def decorator(view_func):
        def wrap(request, *args, **kwargs):
            if request.user.has_perms(permissions):
                return view_func(request, *args, **kwargs)
            else:
                return redirect(redirect_to)
        return wrap
    return decorator



verified_account = login_required

def spielleitung_only(redirect_to="base:index"):
    return _permission_decorator_factory([CustomPermission.SPIELLEITUNG.value], redirect_to=redirect_to)


def LARPler_only(redirect_to="base:index"):
    return _permission_decorator_factory([CustomPermission.LARP.value], redirect_to=redirect_to)

def TODOperson_only(redirect_to="base:index"):
    return _permission_decorator_factory([CustomPermission.SEES_CALENDAR.value], redirect_to=redirect_to)
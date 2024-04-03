from functools import wraps
from urllib.parse import urlparse

from django.shortcuts import redirect, resolve_url
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.auth.views import redirect_to_login

from ppServer import settings


def verified_account(function=None, redirect_field_name=REDIRECT_FIELD_NAME, login_url=None):
    """
    Decorator for views that checks that the user is logged in, redirecting
    to the log-in page if necessary.
    """
    def actual_decorator(view_func):
        @wraps(view_func)
        def _wrapper_view(request, *args, **kwargs):

            # good case:
            if request.user.is_authenticated and request.spieler.is_verified:
                return view_func(request, *args, **kwargs)
            
            # redirect to login:

            path = request.build_absolute_uri()
            resolved_login_url = resolve_url(login_url or settings.LOGIN_URL)
            # If the login url is the same scheme and net location then just
            # use the path as the "next" url.
            login_scheme, login_netloc = urlparse(resolved_login_url)[:2]
            current_scheme, current_netloc = urlparse(path)[:2]
            if (not login_scheme or login_scheme == current_scheme) and (
                not login_netloc or login_netloc == current_netloc
            ):
                path = request.get_full_path()

            return redirect_to_login(path, resolved_login_url, redirect_field_name)

        return _wrapper_view

    return actual_decorator(function) if function else actual_decorator


def spielleiter_only(redirect_to="base:index"):
    def decorator(view_func):
        def wrap(request, *args, **kwargs):
            if request.spieler.is_spielleiter:
                return view_func(request, *args, **kwargs)
            else:
                return redirect(redirect_to)
        return wrap
    return decorator

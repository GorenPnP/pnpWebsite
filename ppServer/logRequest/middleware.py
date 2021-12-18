import re

from .models import Request


class RequestMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.path_blacklist = ("/static", "/media", "/admin")
        self.favicon_filename = "favicon.ico"
        # One-time configuration and initialization.

    def __call__(self, request):
        # Code to be executed for each request before
        # the view (and later middleware) are called.

        if request.scope["path"].startswith(self.path_blacklist) or self.favicon_filename in request.scope["path"]:
            return self.get_response(request)

        response = self.get_response(request)
        Request.objects.create(
            pfad=request.scope["path"],
            antwort=getattr(response, 'status_code', None),
            methode=request.scope["method"],
            user=request.user.username or request.scope["client"][0],
            user_agent=request.META["HTTP_USER_AGENT"]
        )

        return response


from django.utils.deprecation import MiddlewareMixin

from django.http import HttpRequest
from .models import Spieler


class SpielerMiddleware(MiddlewareMixin):
    """ both sync/async Middleware that adds spieler object to each request """

    def process_request(request: HttpRequest):
        request.spieler = None

        if request.user.is_authenticated:
            request.spieler = Spieler.objects.prefetch_related("user").get(user=request.user)

from django.http import HttpRequest
from .models import Spieler


class SpielerMiddleware:
    """ adds spieler object to each request """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request: HttpRequest):
        request.spieler = None

        if request.user.is_authenticated:
            request.spieler = Spieler.objects.prefetch_related("user").get(user=request.user)

        return self.get_response(request)

from django.http import HttpRequest
from .models import Spieler

class RequestSpieler:
    instance: Spieler = None

    is_spielleitung: bool = False
    groups: list[str] = []


class SpielerMiddleware:
    """ adds spieler object & permission information to each request """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request: HttpRequest):
        request.spieler = RequestSpieler()

        if request.user.is_authenticated:
            request.spieler.instance, _ = Spieler.objects.prefetch_related("user__groups").get_or_create(user=request.user)
            request.spieler.groups = [group.name for group in request.spieler.instance.user.groups.all()]
            request.spieler.is_spielleitung = "Spielleitung" in request.spieler.groups

        return self.get_response(request)

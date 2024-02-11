from .models import Spieler

class RequestSpieler:
    instance: Spieler = None

    is_verified: bool = False
    is_spielleiter: bool = False

    groups: list[str] = []


class SpielerMiddleware:
    """ adds spieler object & permission information to each request """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.spieler = RequestSpieler()

        if request.user.is_authenticated:
            request.spieler.instance = Spieler.objects.get(name=request.user.username)
            request.spieler.groups = request.user.groups.values_list("name", flat=True)
            request.spieler.is_verified = len(request.spieler.groups)
            request.spieler.is_spielleiter = "spielleiter" in request.spieler.groups

        return self.get_response(request)

from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import render, get_object_or_404, reverse

from shop.models import Ausrüstung_Technik, Einbauten, Fahrzeug, Item, Magazin, Magische_Ausrüstung, Pfeil_Bolzen,\
                        Rituale_Runen, Rüstungen, Schusswaffen, Waffen_Werkzeuge, Zauber
from character.models import Spieler
from news.models import News
from todays_fact.models import History

# clashing Question-models, so in separate namespaces
import polls.models as pollsm
from quiz.models import SpielerModule


def redirect(request):
    return render(request, "base/redirect.html", {"url": reverse("base:index")})

def reviewable_shop():
    models = [
        Ausrüstung_Technik,
        Einbauten,
        Fahrzeug,
        Item,
        Magazin,
        Magische_Ausrüstung,
        Pfeil_Bolzen,
        Rituale_Runen,
        Rüstungen,
        Schusswaffen,
        Waffen_Werkzeuge,
        Zauber,
    ]

    spielleiter_notes = []
    for m in models:
        for i in m.objects.filter(frei_editierbar=True):
            spielleiter_notes.append({"titel": i.name, "model": m,
                                    "url": reverse('admin:shop_{}_change'.format(m.__name__.lower()), args=(i.id,))})
    return spielleiter_notes


@login_required
def index(request):

    if request.method == "GET":
        spieler = get_object_or_404(Spieler, name=request.user.username)
        context = {"spielleiter": User.objects.filter(username=spieler.name, groups__name='spielleiter').exists(),
                   "topic": "Goren PnP"}


        if context["spielleiter"]:
            context["shop_review"] = reviewable_shop()

        else:
            # all currently open polls, which haven't been answered by the player
            now = timezone.now()
            context["list_vote"] = [q
                for q in pollsm.Question.objects.filter(deadline__gte=now, pub_date__lte=now).order_by('-pub_date')
                if not pollsm.QuestionSpieler.objects.filter(question=q, spieler=spieler).exists()]



        # got open questions in quiz? (state = open)
        context["open_quiz"] = SpielerModule.objects.filter(spieler=spieler, state__in=[2, 4]).exists() # opened or corrected

        context["news"] = News.objects.filter(published=True)[:10]
        context["news_character_count"] = sum([len(n.titel) for n in context["news"]])
        context["todays_fact"] = History.get_fact()

        return render(request, 'base/index.html', context)

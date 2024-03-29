from datetime import datetime

from django.contrib.auth.decorators import login_required
from django.http import HttpResponseNotFound
from django.shortcuts import render, reverse

from changelog.models import Changelog
from shop.models import Alchemie, Ausrüstung_Technik, Begleiter, Einbauten, Engelsroboter, Fahrzeug, Item, Magazin, Magische_Ausrüstung, Pfeil_Bolzen,\
                        Rituale_Runen, Rüstungen, Schusswaffen, Tinker, VergessenerZauber, Waffen_Werkzeuge, Zauber
from character.models import Spieler
from news.models import News
from todays_fact.models import History

# clashing Question-models, so in separate namespaces
import polls.models as pollsm
from quiz.models import SpielerModule


def reviewable_shop():
    models = [
        Alchemie,
        Ausrüstung_Technik,
        Begleiter,
        Einbauten,
        Engelsroboter,
        Fahrzeug,
        Item,
        Magazin,
        Magische_Ausrüstung,
        Pfeil_Bolzen,
        Rituale_Runen,
        Rüstungen,
        Schusswaffen,
        Tinker,
        VergessenerZauber,
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
        spieler = request.spieler.instance
        if not spieler: return HttpResponseNotFound()

        context = {
            "topic": "Goren PnP",
            "latest_update": Changelog.objects.first()
        }


        if request.spieler.is_spielleiter:
            context["shop_review"] = reviewable_shop()

        else:
            now = datetime.now()

            # all currently open polls, which haven't been answered by the player
            context["list_vote"] = [q
                for q in pollsm.Question.objects.filter(deadline__gte=now, pub_date__lte=now).order_by('-pub_date')
                if not pollsm.QuestionSpieler.objects.filter(question=q, spieler=spieler).exists()]



        # got open questions in quiz? (state = open)
        context["open_quiz"] = SpielerModule.objects.filter(spieler=spieler, state__in=[2, 4]).exists() # opened or corrected

        context["news"] = News.objects.filter(published=True)[:10]
        context["news_character_count"] = sum([len(n.titel) for n in context["news"]])
        context["todays_fact"] = History.get_fact()

        # collect topics for hero
        context["hero_pages"] = ["Fun Fact"]
        if "list_vote" in context and len(context["list_vote"]):  context["hero_pages"].append("Umfrage")
        if "open_quiz" in context and context["open_quiz"]:  context["hero_pages"].append("Quiz")
        context["hero_pages"].append("Schmiedesystem")
        if "shop_review" in context and len(context["shop_review"]):  context["hero_pages"].append("Shop review")

        return render(request, 'base/index.html', context)

from datetime import datetime
from typing import Any

from django.shortcuts import reverse
from django.views.generic.base import TemplateView

from changelog.models import Changelog
from ppServer.mixins import VerifiedAccountMixin
from shop.models import Alchemie, Ausrüstung_Technik, Begleiter, Einbauten, Engelsroboter, Fahrzeug, Item, Magazin, Magische_Ausrüstung, Pfeil_Bolzen,\
                        Rituale_Runen, Rüstungen, Schusswaffen, Tinker, VergessenerZauber, Waffen_Werkzeuge, Zauber
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

    spielleitung_notes = []
    for m in models:
        for i in m.objects.filter(frei_editierbar=True):
            spielleitung_notes.append({"titel": i.name, "model": m,
                                    "url": reverse('admin:shop_{}_change'.format(m.__name__.lower()), args=(i.id,))})
    return spielleitung_notes


class IndexView(VerifiedAccountMixin, TemplateView):
    template_name = "base/index.html"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(
            **kwargs,
            topic = "Goren PnP",
            latest_update = Changelog.objects.first(),
            news = News.objects.filter(published=True)[:10],
            todays_fact = History.get_fact(),
        )

        return {
            **context,
            **self.get_heros(),
            "news_character_count": sum([len(n.titel) for n in context["news"]])
        }
    
    def get_heros(self):
        #### collect topics for hero ####

        spieler = self.request.spieler.instance

        context = { "hero_pages": ["Fun Fact", "Regeln"], }

        ## polls
        if not self.request.spieler.is_spielleitung:
            now = datetime.now()

            # all currently open polls, which haven't been answered by the player
            question = pollsm.Question.objects\
                .filter(deadline__gte=now, pub_date__lte=now)\
                .exclude(questionspieler__spieler=spieler)\
                .order_by('-pub_date')\
                .first()
            if question:
                context["poll_question"] = question
                context["hero_pages"].append("Umfrage")
        
        ## quiz
        # got open questions in quiz? (state = opened or corrected)
        if SpielerModule.objects.filter(spieler=spieler, state__in=[2, 4]).exists():
            context["hero_pages"].append("Quiz")

        ## schmiedesystem
        context["hero_pages"].append("Schmiedesystem")

        ## shop review
        if self.request.spieler.is_spielleitung:
            shop = reviewable_shop()
            if len(shop): context["hero_pages"].append("Shop review")

        return context


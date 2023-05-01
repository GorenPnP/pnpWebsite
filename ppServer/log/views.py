from django.contrib.admin.models import LogEntry
from django.contrib.auth.mixins import LoginRequiredMixin

from base.abstract_views import DynamicTableView, GenericTable
from ppServer.mixins import SpielleiterOnlyMixin

from .models import Log


def logShop(spieler, char, items):
    """Gekaufte Items"""
    """items = [{"num": , "item_str": , (ggf. "stufe": ,) "preis_ges": , (ggf. "preisCP_ges": ,) "firma_titel": , "in_points": }]"""

    for i in items:

        if i["num"] <= 0:
            raise ValueError("Item {}: die gekaufte Anzahl ist negativ".format(i["item"].__str__()))

        if i["preis_ges"] < 0:
            raise ValueError("Item {}: der bezahlte Preis in Drachmen oder Quiz-Punkten ist negativ".format(i["item"].__str__()))

        notizen = "Von {} wurden {} Stück".format(i["item"].__str__(), i["num"])
        if i["item"].stufenabhängig:
            notizen += " der Stufe {}".format( i["stufe"])
        notizen += " von der Firma {} gekauft.".format(i["firma_titel"])

        kosten = "{} Drachmen".format(i["preis_ges"])

        Log.objects.create(art="s", spieler=spieler, char=char, notizen=notizen, kosten=kosten)


def logQuizPointsSP(spieler, char, quiz_points_alt, quiz_points_neu, neue_sp, notiz=None):
    """Vermehrung des Geldes"""
    if quiz_points_neu > quiz_points_alt:
        raise ValueError("Der Betrag der Punkte ist größer geworden")

    kosten = "{} Quiz-Punkte".format(quiz_points_alt - quiz_points_neu)

    notizen = "Der Charakter besitzt nun {} SP mehr, also {}.".format(neue_sp, neue_sp + char.sp)
    if notiz:
        notizen += "\n" + notiz

    Log.objects.create(art="d", spieler=spieler, char=char, notizen=notizen, kosten=kosten)

def logAlleMAverloren(spieler, char, rel_MA, spruchz_fp, kampfm_fp, antim_fp):
    """Die Magie ist (mal wieder) komplett weg"""

    notizen = "Der Charakter besitzt nun komplett keine Magie Mehr.\n"
    kosten = 0
    # attr (aktuell, max)
    if rel_MA.aktuellerWert > 0 or rel_MA.maxWert > 0:
        notizen += "Magie-Attribut: "

    if rel_MA.aktuellerWert > 0:
        notizen += "aktueller Wert -{}, ".format(rel_MA.aktuellerWert)
        kosten += (rel_MA.aktuellerWert * 3)

    if rel_MA.maxWert > 0:
        notizen += "Maximum -{},".format(rel_MA.maxWert)
        kosten += (rel_MA.maxWert * 5)

    notizen += "\n"

    # fg
    if rel_MA.fg > 0:
        notizen += "FG der Magie: -{},\n".format(rel_MA.fg)
        kosten += (rel_MA.fg * 2)

    # fp
    if spruchz_fp > 0:
        notizen += "Spruchzauberei-FP: -{},\n".format(spruchz_fp)
        kosten += spruchz_fp

    if kampfm_fp > 0:
        notizen += "Kampfmagie-FP: -{},\n".format(kampfm_fp)
        kosten += kampfm_fp

    if antim_fp > 0:
        notizen += "Antimagie-FP: -{}".format(antim_fp)
        kosten += antim_fp

    Log.objects.create(art="v", spieler=spieler, char=char, notizen=notizen, kosten="{} CP".format(kosten))



class UserLogView(LoginRequiredMixin, SpielleiterOnlyMixin, DynamicTableView):
    model = Log
    filterset_fields = {
        "char": ["exact"],
        "spieler": ["exact"],
        "art": ["icontains"],
        "notizen": ["icontains"],
        "kosten": ["icontains"],
        "timestamp": ["lte"],
    }
    table_fields = ["char", "spieler", "art", "notizen", "kosten", "timestamp"]

    def get_app_index(self): return None
    def get_app_index_url(self): return None


class AdminLogView(LoginRequiredMixin, SpielleiterOnlyMixin, DynamicTableView):
    class Table(GenericTable):
        class Meta:
            model = LogEntry
            fields = ["action_time", "user", "object_repr", "change_message"]
            attrs= {"class": "table table-dark table-striped table-hover"}

        def render_change_message(self, value, record):
            return record.get_change_message()

    model = LogEntry
    queryset = LogEntry.objects.exclude(user__username="spielleiter").filter(content_type__app_label="character", content_type__model="charakter")
    
    topic = "Changes in Admin area"
    filterset_fields = {"action_time": ["lte"], "user": ["exact"], "object_repr": ["icontains"], "change_message": ["icontains"]}
    table_class = Table
    
    def get_app_index(self): return None
    def get_app_index_url(self): return None

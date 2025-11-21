import random
from datetime import date

from django.db.models import Case, When, PositiveIntegerField, Q
from django.contrib import messages
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import DetailView
from django.urls import reverse

from cards.models import Card, Transaction
from character.models import *
from log.create_log import logShop
from ppServer.mixins import VerifiedAccountMixin

from ..models import *


class BuyView(VerifiedAccountMixin, DetailView):
    class Meta:
        abstract = True

    template_name = "shop/buy_shop.html"

    shop_model = None
    relshop_model = None
    firmashop_model = None
    relfirmashop_model = None

    def get(self, request, id=int, *args, **kwargs):

        firma_shop_entries = self.firmashop_model.objects.filter(item=id)
        item = get_object_or_404(self.shop_model, id=id)

        charaktere = Charakter.objects.all()

        # characters to buy stuff for
        if not request.spieler.is_spielleitung:
            if self.shop_model._meta.model_name == "zauber":
                charaktere = charaktere.annotate(
                        # mind. 5 bei Zaubern:
                        magieamateur_exists = Exists(RelVorteil.objects.filter(char=OuterRef("pk"), teil__titel="Magie-Amateur")),                    
                        # mind. 10 bei Zaubern:
                        magiegelehrter_exists = Exists(RelVorteil.objects.filter(char=OuterRef("pk"), teil__titel="Magie-Gelehrter")),

                        max_shopstufe=Case(When(
                            Q(magiegelehrter_exists=True) & Q(ep_stufe_in_progress__lt=10),
                            then=10),
                            default=Case(When(
                                Q(magieamateur_exists=True) & Q(ep_stufe_in_progress__lt=5),
                                then=5),
                                default=F("ep_stufe_in_progress"),
                                output_field=PositiveIntegerField()
                            ),
                            output_field=PositiveIntegerField()
                        ),
                    )
            else:
                charaktere = charaktere.annotate(
                    # mind. 3
                    basarflipper_exists = Exists(RelVorteil.objects.filter(char=OuterRef("pk"), teil__titel="Basar-Flipper")),
                    max_shopstufe=Case(When(Q(basarflipper_exists=True) & Q(ep_stufe_in_progress__lt=3), then=3), default=F("ep_stufe_in_progress"), output_field=PositiveIntegerField()), #F("ep_stufe_in_progress"),
                )

            charaktere = charaktere.filter(eigentümer=request.spieler.instance, max_shopstufe__gte=item.ab_stufe)

        context = {
            "charaktere": charaktere.order_by('name'),
            "entries": firma_shop_entries,
            "extra_preis_field": request.spieler.is_spielleitung,
            "st": item.stufenabhängig,
            "topic": item.name,
            "app_index": "Shop",
            "app_index_url": reverse("shop:index")
        }

        # for redirect eventually
        context["text"] = "Für dieses Item gibt es keinen Verkäufer."
        return render(request, self.template_name, context)
    
    def post(self, request, id: int):
        # def buy_item_post(rit_run=False):
        item = self.shop_model.objects.get(id=id)

        # free unused space (random, I know ...)
        self.relfirmashop_model.objects.exclude(last_tried=date.today()).delete()

        # retrieve all values from request.POST & check them
        extra = char_id = num_items = firma_shop_id = price = stufe = -2
        try:
            extra = "extra" in request.POST
            char_id = int(request.POST.get("character"))
            num_items = int(request.POST.get('amount'))
            firma_shop_id = int(request.POST.get('firmashop_id')) if not extra else None
            price = int(request.POST.get('price')) if extra else None
            stufe = int(request.POST.get("stufe")) if request.POST.get("stufe") else None
        except:
            messages.error(request, "Daten nicht vollständig erhalten")
            return redirect(request.build_absolute_uri())

        # check if spieler may modify char
        spieler = request.spieler.instance
        char = get_object_or_404(Charakter, id=char_id)
        if char.eigentümer != spieler and not request.spieler.is_spielleitung:
            messages.error(request, "Keine Erlaubnis einzukaufen")
            return redirect(request.build_absolute_uri())

        if not extra:
            firma_shop = get_object_or_404(self.firmashop_model, id=firma_shop_id)
            if (firma_shop.item.stufenabhängig or self.shop_model == Rituale_Runen) and stufe is None:
                messages.error(request, "Die Stufe ist nicht angekommen")
                return redirect(request.build_absolute_uri())

            # tried today already?
            if not char.in_erstellung and self.relfirmashop_model.objects.filter(char=char, firma_shop=firma_shop, last_tried=date.today()).exists():
                messages.error(request, "Heute kommt keine neue Ware mehr. Versuch's doch morgen nochmal.")
                return redirect(request.build_absolute_uri())


        # is the money all right?

        # price of one item (at Stufe 1)
        if extra: debt = price
        elif self.shop_model == Rituale_Runen: debt = getattr(firma_shop, "getPriceStufe{}".format(stufe))()
        else: debt = firma_shop.getPrice()

        # multiply num_items and stufe
        if item.stufenabhängig and not self.shop_model == Rituale_Runen: debt *= num_items * stufe
        else: debt *= num_items

        if debt > char.geld:
            messages.error(request, "Du bist zu arm dafür")
            return redirect(request.build_absolute_uri())


        # how about verfgbarkeit?
        if not char.in_erstellung and not extra:
            verf = firma_shop.verfügbarkeit
            if item.stufenabhängig: verf -= (stufe - 1) * 10

            rand = random.randint(1, 100)

            # not available, try tomorrow
            if  rand > verf:
                # add mark for today's unsuccessful try
                self.relfirmashop_model.objects.create(char=char, firma_shop=firma_shop)

                messages.error(request, "Mit einer Verfügbarkeit von {} und einem random Wert von {} darüber ist es nicht verfügbar.".format(verf, rand) +\
                    " Try again tomorrow")
                return redirect(request.build_absolute_uri())


        # add to db or increase num if already exists

        # stufenabhängig
        if item.stufenabhängig or self.shop_model == Rituale_Runen:
            items = self.relshop_model.objects.filter(char=char, item=item, stufe=stufe)
            if items.count():
                i = items[0]
                i.anz += num_items

                i.save(update_fields=["anz"])
            else:
                self.relshop_model.objects.create(char=char, item=item, stufe=stufe, anz=num_items)

        # stufenUNabhängig
        else:
            items = self.relshop_model.objects.filter(char=char, item=item)
            if items.count():
                i = items[0]
                i.anz += num_items

                i.save(update_fields=["anz"])
            else:
                self.relshop_model.objects.create(char=char, item=item, anz=num_items)

        # pay
        char.card.money -= debt
        char.card.save(update_fields=["money"])
        spielleitung_spieler = get_object_or_404(Spieler, name__startswith="spielleit")
        firma_card = None if extra else Card.objects.get_or_create(name=firma_shop.firma.name, spieler=spielleitung_spieler)[0]
        Transaction.objects.create(sender=char.card, receiver=firma_card, amount=debt, reason=f"kaufe {num_items}x {item.name}{' Stufe {}'.format(stufe) if item.stufenabhängig else ''}")

        # log
        log_dict = {
            "num": num_items, "item": item, "preis_ges": debt,
            "firma_titel": firma_shop.firma.name if not extra else "außer der Reihe", "stufe": stufe}
        logShop(spieler, char, log_dict)


        messages.success(request, f"{char.name} hat {debt} Dr. für {num_items} Item(s) ausgegeben.")
        return redirect(request.build_absolute_uri())






# specific buy_shop
class ItemBuyView(BuyView):
    shop_model = Item
    relshop_model = RelItem
    firmashop_model = FirmaItem
    relfirmashop_model = RelFirmaItem

class Waffen_WerkzeugeBuyView(BuyView):
    shop_model = Waffen_Werkzeuge
    relshop_model = RelWaffen_Werkzeuge
    firmashop_model = FirmaWaffen_Werkzeuge
    relfirmashop_model = RelFirmaWaffen_Werkzeuge

class MagazinBuyView(BuyView):
    shop_model = Magazin
    relshop_model = RelMagazin
    firmashop_model = FirmaMagazin
    relfirmashop_model = RelFirmaMagazin

class Pfeil_BolzenBuyView(BuyView):
    shop_model = Pfeil_Bolzen
    relshop_model = RelPfeil_Bolzen
    firmashop_model = FirmaPfeil_Bolzen
    relfirmashop_model = RelFirmaPfeil_Bolzen

class SchusswaffenBuyView(BuyView):
    shop_model = Schusswaffen
    relshop_model = RelSchusswaffen
    firmashop_model = FirmaSchusswaffen
    relfirmashop_model = RelFirmaSchusswaffen

class Rituale_RunenBuyView(BuyView):
    shop_model = Rituale_Runen
    relshop_model = RelRituale_Runen
    firmashop_model = FirmaRituale_Runen
    relfirmashop_model = RelFirmaRituale_Runen

    template_name = "shop/buy_rituale_runen.html"

class Magische_AusrüstungBuyView(BuyView):
    shop_model = Magische_Ausrüstung
    relshop_model = RelMagische_Ausrüstung
    firmashop_model = FirmaMagische_Ausrüstung
    relfirmashop_model = RelFirmaMagische_Ausrüstung

class RüstungBuyView(BuyView):
    shop_model = Rüstungen
    relshop_model = RelRüstung
    firmashop_model = FirmaRüstungen
    relfirmashop_model = RelFirmaRüstung

class Ausrüstung_TechnikBuyView(BuyView):
    shop_model = Ausrüstung_Technik
    relshop_model = RelAusrüstung_Technik
    firmashop_model = FirmaAusrüstung_Technik
    relfirmashop_model = RelFirmaAusrüstung_Technik

class FahrzeugBuyView(BuyView):
    shop_model = Fahrzeug
    relshop_model = RelFahrzeug
    firmashop_model = FirmaFahrzeug
    relfirmashop_model = RelFirmaFahrzeug

class EinbautenBuyView(BuyView):
    shop_model = Einbauten
    relshop_model = RelEinbauten
    firmashop_model = FirmaEinbauten
    relfirmashop_model = RelFirmaEinbauten

class ZauberBuyView(BuyView):
    shop_model = Zauber
    relshop_model = RelZauber
    firmashop_model = FirmaZauber
    relfirmashop_model = RelFirmaZauber

class VergessenerZauberBuyView(BuyView):
    shop_model = VergessenerZauber
    relshop_model = RelVergessenerZauber
    firmashop_model = FirmaVergessenerZauber
    relfirmashop_model = RelFirmaVergessenerZauber

class AlchemieBuyView(BuyView):
    shop_model = Alchemie
    relshop_model = RelAlchemie
    firmashop_model = FirmaAlchemie
    relfirmashop_model = RelFirmaAlchemie

class BegleiterBuyView(BuyView):
    shop_model = Begleiter
    relshop_model = RelBegleiter
    firmashop_model = FirmaBegleiter
    relfirmashop_model = RelFirmaBegleiter

class EngelsroboterBuyView(BuyView):
    shop_model = Engelsroboter
    relshop_model = RelEngelsroboter
    firmashop_model = FirmaEngelsroboter
    relfirmashop_model = RelFirmaEngelsroboter

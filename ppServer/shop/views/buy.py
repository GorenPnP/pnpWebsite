import random, json
from datetime import date
from typing import Any

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http.response import JsonResponse
from django.shortcuts import render, get_object_or_404

from character.models import *
from log.views import logShop
from ppServer.decorators import verified_account

from ..models import *


# specific buy_shop
@login_required
@verified_account
def buy_item(request, id):
    if request.method == 'GET':
        context = buy_item_get(request, id, Item, RelItem, FirmaItem)
        return render(request, "shop/buy_shop.html", context)

    if request.method == 'POST':
        item = get_object_or_404(Item, id=id)
        return buy_item_post(request, item, FirmaItem, RelItem, RelFirmaItem)


@login_required
@verified_account
def buy_waffen_werkzeuge(request, id):
    if request.method == 'GET':
        context = buy_item_get(request, id, Waffen_Werkzeuge ,RelWaffen_Werkzeuge, FirmaWaffen_Werkzeuge)
        return render(request, "shop/buy_shop.html", context)

    if request.method == 'POST':
        item = get_object_or_404(Waffen_Werkzeuge, id=id)
        return buy_item_post(request, item, FirmaWaffen_Werkzeuge, RelWaffen_Werkzeuge, RelFirmaWaffen_Werkzeuge)


@login_required
@verified_account
def buy_magazin(request, id):
    if request.method == 'GET':
        context = buy_item_get(request, id, Magazin, RelMagazin, FirmaMagazin)
        return render(request, "shop/buy_shop.html", context)

    if request.method == 'POST':
        item = get_object_or_404(Magazin, id=id)
        return buy_item_post(request, item, FirmaMagazin, RelMagazin, RelFirmaMagazin)


@login_required
@verified_account
def buy_pfeil_bolzen(request, id):
    if request.method == 'GET':
        context = buy_item_get(request, id, Pfeil_Bolzen, RelPfeil_Bolzen, FirmaPfeil_Bolzen)
        return render(request, "shop/buy_shop.html", context)

    if request.method == 'POST':
        item = get_object_or_404(Pfeil_Bolzen, id=id)
        return buy_item_post(request, item, FirmaPfeil_Bolzen, RelPfeil_Bolzen, RelFirmaPfeil_Bolzen)


@login_required
@verified_account
def buy_schusswaffe(request, id):
    if request.method == 'GET':
        context = buy_item_get(request, id, Schusswaffen, RelSchusswaffen, FirmaSchusswaffen)
        return render(request, "shop/buy_shop.html", context)

    if request.method == 'POST':
        item = get_object_or_404(Schusswaffen, id=id)
        return buy_item_post(request, item, FirmaSchusswaffen, RelSchusswaffen, RelFirmaSchusswaffen)


@login_required
@verified_account
def buy_rituale_runen(request, id):
    spieler = get_object_or_404(Spieler, name=request.user.username)

    if request.method == 'GET':
        context = buy_item_get(request, id, Rituale_Runen, RelRituale_Runen, FirmaRituale_Runen)
        return render(request, "shop/buy_rituale_runen.html", context)

    if request.method == 'POST':
        item = get_object_or_404(Rituale_Runen, id=id)
        return buy_item_post(request, item, FirmaRituale_Runen, RelRituale_Runen, RelFirmaRituale_Runen, rit_run=True)


@login_required
@verified_account
def buy_magische_ausrüstung(request, id):
    if request.method == 'GET':
        context = buy_item_get(request, id, Magische_Ausrüstung, RelMagische_Ausrüstung, FirmaMagische_Ausrüstung)
        return render(request, "shop/buy_shop.html", context)

    if request.method == 'POST':
        item = get_object_or_404(Magische_Ausrüstung, id=id)
        return buy_item_post(request, item, FirmaMagische_Ausrüstung, RelMagische_Ausrüstung, RelFirmaMagische_Ausrüstung)


@login_required
@verified_account
def buy_rüstung(request, id):
    if request.method == 'GET':
        context = buy_item_get(request, id, Rüstungen, RelRüstung, FirmaRüstungen)
        return render(request, "shop/buy_shop.html", context)

    if request.method == 'POST':
        item = get_object_or_404(Rüstungen, id=id)
        return buy_item_post(request, item, FirmaRüstungen, RelRüstung, RelFirmaRüstung)


@login_required
@verified_account
def buy_ausrüstung_technik(request, id):
    if request.method == 'GET':
        context = buy_item_get(request, id, Ausrüstung_Technik , RelAusrüstung_Technik, FirmaAusrüstung_Technik)
        return render(request, "shop/buy_shop.html", context)

    if request.method == 'POST':
        item = get_object_or_404(Ausrüstung_Technik, id=id)
        return buy_item_post(request, item, FirmaAusrüstung_Technik, RelAusrüstung_Technik, RelFirmaAusrüstung_Technik)


@login_required
@verified_account
def buy_fahrzeug(request, id):
    if request.method == 'GET':
        context = buy_item_get(request, id, Fahrzeug, RelFahrzeug, FirmaFahrzeug)
        return render(request, "shop/buy_shop.html", context)

    if request.method == 'POST':
        item = get_object_or_404(Fahrzeug, id=id)
        return buy_item_post(request, item, FirmaFahrzeug, RelFahrzeug, RelFirmaFahrzeug)


@login_required
@verified_account
def buy_einbauten(request, id):
    if request.method == 'GET':
        context = buy_item_get(request, id, Einbauten, RelEinbauten, FirmaEinbauten)
        return render(request, "shop/buy_shop.html", context)

    if request.method == 'POST':
        item = get_object_or_404(Einbauten, id=id)
        return buy_item_post(request, item, FirmaEinbauten, RelEinbauten, RelFirmaEinbauten)


@login_required
@verified_account
def buy_zauber(request, id):
    if request.method == 'GET':
        context = buy_item_get(request, id, Zauber, RelZauber, FirmaZauber)
        return render(request, "shop/buy_shop.html", context)

    if request.method == 'POST':
        item = get_object_or_404(Zauber, id=id)
        return buy_item_post(request, item, FirmaZauber, RelZauber, RelFirmaZauber)


@login_required
@verified_account
def buy_vergessener_zauber(request, id):
    if request.method == 'GET':
        context = buy_item_get(request, id, VergessenerZauber, RelVergessenerZauber, FirmaVergessenerZauber)
        return render(request, "shop/buy_shop.html", context)

    if request.method == 'POST':
        item = get_object_or_404(VergessenerZauber, id=id)
        return buy_item_post(request, item, FirmaVergessenerZauber, RelVergessenerZauber, RelFirmaVergessenerZauber)


@login_required
@verified_account
def buy_alchemie(request, id):
    if request.method == 'GET':
        context = buy_item_get(request, id, Alchemie, RelAlchemie, FirmaAlchemie)
        return render(request, "shop/buy_shop.html", context)

    if request.method == 'POST':
        item = get_object_or_404(Alchemie, id=id)
        return buy_item_post(request, item, FirmaAlchemie, RelAlchemie, RelFirmaAlchemie)


@login_required
@verified_account
def buy_begleiter(request, id):
    if request.method == 'GET':
        context = buy_item_get(request, id, Begleiter, RelBegleiter, FirmaBegleiter)
        return render(request, "shop/buy_shop.html", context)

    if request.method == 'POST':
        item = get_object_or_404(Begleiter, id=id)
        return buy_item_post(request, item, FirmaBegleiter, RelBegleiter, RelFirmaBegleiter)


# generic things for bying item in shop
def buy_item_get(request, id, shop_model, rel_shop_model, firma_shop_model):
    firma_shop_entries = firma_shop_model.objects.filter(item__id=id)
    item = get_object_or_404(shop_model, id=id)

    extra_preis_field = User.objects.filter(username=request.user.username, groups__name='spielleiter').exists()
    if extra_preis_field:
        charaktere = Charakter.objects.all().order_by('name')
    else:
        charaktere = Charakter.objects.filter(eigentümer__name=request.user.username).order_by('name')

    context = {"charaktere": charaktere, "entries": firma_shop_entries, "topic": item.name,
               "extra_preis_field": extra_preis_field, "st": item.stufenabhängig}

    # for redirect eventually
    context["text"] = "Für dieses Item gibt es keinen Verkäufer."
    return context


def buy_item_post(request, item, firma_shop_model, rel_shop_model, verf_model, rit_run=False):

    # free unused space (random, I know ...)
    verf_model.objects.exclude(last_tried=date.today()).delete()

    # retrieve all values from request.POST & check them
    extra = notizen = char_id = num_items = firma_shop_id = price = stufe = -2
    try:
        data = json.loads(request.body.decode("utf-8"))

        extra = data["extra"]
        notizen = data['notizen']
        char_id = int(data["char"])
        num_items = int(data['num'])
        firma_shop_id = int(data['firma_shop']) if not extra else None
        price = int(data['price']) if extra else None
        stufe = int(data["stufe"]) if data["stufe"] else None
    except:
        return JsonResponse({"message": "Daten nicht vollständig erhalten"}, status=418)

    # check if spieler may modify char
    spieler = get_object_or_404(Spieler, name=request.user.username)
    char = get_object_or_404(Charakter, id=char_id)
    if char.eigentümer != spieler and not User.objects.filter(username=request.user.username, groups__name='spielleiter').exists():
        return JsonResponse({"message": "Keine Erlaubnis einzukaufen"}, status=418)

    if not extra:
        firma_shop = get_object_or_404(firma_shop_model, id=firma_shop_id)
        if (firma_shop.item.stufenabhängig or rit_run) and stufe is None:
            return JsonResponse({"message": "Die Stufe ist nicht angekommen"}, status=418)

        # tried today already?
        if not char.in_erstellung and verf_model.objects.filter(char=char, firma_shop=firma_shop, last_tried=date.today()).exists():
            return JsonResponse({"message": "Heute kommt keine neue Ware mehr. Versuch's doch morgen nochmal."}, status=418)


    # is the money all right?

    # price of one item (at Stufe 1)
    if extra: debt = price
    elif rit_run: debt = getattr(firma_shop, "getPriceStufe{}".format(stufe))()
    else: debt = firma_shop.getPrice()

    # multiply num_items and stufe
    if item.stufenabhängig and not rit_run: debt *= num_items * stufe
    else: debt *= num_items

    if debt > char.geld:
        return JsonResponse({"message": "Du bist zu arm dafür"}, status=418)


    # how about verfgbarkeit?
    if not char.in_erstellung and not extra:
        verf = firma_shop.verfügbarkeit
        if item.stufenabhängig: verf -= (stufe - 1) * 10

        rand = random.randint(1, 100)

        # not available, try tomorrow
        if  rand > verf:
            # add mark for today's unsuccessful try
            verf_model.objects.create(char=char, firma_shop=firma_shop)

            return JsonResponse({"message":
                "Mit einer Verfügbarkeit von {} und einem random Wert von {} darüber ist es nicht verfügbar.".format(verf, rand) +\
                " Try again tomorrow"}, status=418)


    # add to db or increase num if already exists

    # stufenabhängig
    if item.stufenabhängig or rit_run:
        items = rel_shop_model.objects.filter(char=char, item=item, stufe=stufe)
        if items.count():
            i = items[0]
            i.anz += num_items
            if notizen and len(notizen): i.notizen = ", ".join([i.notizen, notizen])

            i.save()
        else:
            rel_shop_model.objects.create(char=char, item=item, stufe=stufe, anz=num_items, notizen=notizen)

    # stufenUNabhängig
    else:
        items = rel_shop_model.objects.filter(char=char, item=item)
        if items.count():
            i = items[0]
            i.anz += num_items
            if notizen and len(notizen): i.notizen = ", ".join([i.notizen, notizen])

            i.save()
        else:
            rel_shop_model.objects.create(char=char, item=item, anz=num_items, notizen=notizen)

    # pay
    char.geld -= debt
    char.save()

    # log
    log_dict = {"num": num_items, "item": item, "preis_ges": debt,
                "firma_titel": firma_shop.firma.name if not extra else "außer der Reihe", "stufe": stufe}
    logShop(spieler, char, [log_dict])

    # notify about money change
    response_data = {"character": char.name, "old": char.geld + debt,
                        "new": char.geld, 'preis': debt}
    return JsonResponse(response_data)

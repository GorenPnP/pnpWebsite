from ppServer.decorators import verified_account
import random, json, re
import sre_constants

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http.response import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.utils.datetime_safe import date

from log.views import logShop
from character.models import *
from base.views import reviewable_shop
from ppServer.decorators import spielleiter_only

from .models import *


@login_required
@spielleiter_only()
def review_items(request):

    if not request.user.groups.filter(name="spielleiter").exists():
        return redirect("base:index")

    context = {"topic": "Neue Items", "items": reviewable_shop()}

    if not context["items"]:
        return redirect("base:index")

    return render(request, "shop/review_items.html", context)


@login_required
@verified_account
def index(request):
    if request.method == "GET":
        return render(request, "shop/index.html", {"topic": "Shop"})

    if request.method == "POST":
        try:
            search_text = json.loads(request.body.decode("utf-8"))["search_text"]
        except:
            return JsonResponse({"message": "Suchtext ist nicht angekommen"}, status=418)

        if len(search_text) == 0: return JsonResponse({"item_list": []})
        try:
            re.compile(search_text)
        except sre_constants.error as e:
            search_text = re.escape(search_text)

        item_list = []
        model_list = [
                      (Item, "items"),
                      (Waffen_Werkzeuge, "waffen_werkzeuge"),
                      (Magazin, "magazine"),
                      (Pfeil_Bolzen, "pfeile_bolzen"),
                      (Schusswaffen, "schusswaffen"),
                      (Magische_Ausrüstung, "mag_ausrüstung"),
                      (Rituale_Runen, "rituale_runen"),
                      (Rüstungen, "rüstungen"),
                      (Ausrüstung_Technik, "ausr_technik"),
                      (Fahrzeug, "fahrzeuge"),
                      (Einbauten, "einbauten"),
                      (Zauber, "zauber"),
                      (VergessenerZauber, "vergessene_zauber"),
                      (Alchemie, "alchemie"),
                      (Tinker, "tinker"),
                    ]
        for model, url_frag in model_list:
            for item in model.objects.filter(name__iregex=search_text, frei_editierbar__exact=False):
                view = "shop:{}".format(url_frag)
                item_list.append({"name": item.__str__(), "url": "{}#{}".format(reverse(view), item.id)})

        return JsonResponse({"item_list": item_list})


# specific show_shop
@login_required
@verified_account
def item(request):
    return show_shop(request, "Items", Item, FirmaItem, reverse("admin:shop_item_add"))


@login_required
@verified_account
def waffen_werkzeuge(request):
    return show_shop(request, "Waffen & Werkzeuge", Waffen_Werkzeuge, FirmaWaffen_Werkzeuge, reverse("admin:shop_waffen_werkzeuge_add"))


@login_required
@verified_account
def magazine(request):
    return show_shop(request, "Magazine", Magazin, FirmaMagazin, reverse("admin:shop_magazin_add"))


@login_required
@verified_account
def pfeile_bolzen(request):
    return show_shop(request, "Pfeile & Bolzen", Pfeil_Bolzen, FirmaPfeil_Bolzen, reverse("admin:shop_pfeil_bolzen_add"))


@login_required
@verified_account
def schusswaffen(request):
    return show_shop(request, "Schusswaffen", Schusswaffen, FirmaSchusswaffen, reverse("admin:shop_schusswaffen_add"))


@login_required
@verified_account
def mag_ausrüstung(request):
    return show_shop(request, "Magische Ausrüstung", Magische_Ausrüstung, FirmaMagische_Ausrüstung, reverse("admin:shop_magische_ausrüstung_add"))


@login_required
@verified_account
def rituale_runen(request):
    return show_shop(request, "Rituale & Runen", Rituale_Runen, FirmaRituale_Runen, reverse("admin:shop_rituale_runen_add"))


@login_required
@verified_account
def rüstungen(request):
    return show_shop(request, "Rüstungen", Rüstungen, FirmaRüstungen, reverse("admin:shop_rüstungen_add"))


@login_required
@verified_account
def ausrüstung_technik(request):
    return show_shop(request, "Ausrüstung & Technik", Ausrüstung_Technik, FirmaAusrüstung_Technik, reverse("admin:shop_ausrüstung_technik_add"))


@login_required
@verified_account
def fahrzeuge(request):
    return show_shop(request, "Fahrzeuge", Fahrzeug, FirmaFahrzeug, reverse("admin:shop_fahrzeug_add"))


@login_required
@verified_account
def einbauten(request):
    return show_shop(request, "Einbauten", Einbauten, FirmaEinbauten, reverse("admin:shop_einbauten_add"))


@login_required
@verified_account
def zauber(request):
    return show_shop(request, "Zauber", Zauber, FirmaZauber, reverse("admin:shop_zauber_add"))


@login_required
@verified_account
def vergessene_zauber(request):
    return show_shop(request, "Vergessene Zauber", VergessenerZauber, FirmaVergessenerZauber, reverse("admin:shop_vergessenerzauber_add"))


@login_required
@verified_account
def alchemie(request):
    return show_shop(request, "Alchemie", Alchemie, FirmaAlchemie, reverse("admin:shop_alchemie_add"))


@login_required
@verified_account
def tinker(request):
    return show_shop(request, "Für Selbstständige", Tinker, FirmaTinker, reverse("admin:shop_tinker_add"))


# generic show_shop
def show_shop(request, topic, shop_model, firma_shop_model, plus_url=""):

    # get min + max ep from filter
    try:
        min_ep_rang = int(request.GET.get("min_ep_rang"))
    except: min_ep_rang = -1
    try:
        max_ep_rang = int(request.GET.get("max_ep_rang"))
    except: max_ep_rang = 1000

    # collect fields for table
    fields = [shop_model.get_fields()]

    items = shop_model.objects.filter(frei_editierbar=False, ab_stufe__gte=min_ep_rang, ab_stufe__lte=max_ep_rang).order_by("name")
    for i in items:
        fields.append(i.get_values(firma_shop_model))

    context = {"fields": fields, "topic": topic, "min_ep_rang": min_ep_rang if min_ep_rang != -1 else None,
               "max_ep_rang": max_ep_rang if max_ep_rang != 1000 else None, "plus_url": plus_url}
    return render(request, "shop/show.html", context)


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
def buy_mag_ausrüstung(request, id):
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
    elif rit_run: debt = getattr(firma_shop, "stufe_{}".format(stufe))
    else: debt = firma_shop.current_price()

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

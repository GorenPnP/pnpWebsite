import random
from datetime import date

from django.apps import apps
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import DetailView

from cards.models import Card, Transaction
from character.models import *
from log.create_log import logShop
from ppServer.mixins import VerifiedAccountMixin

from ..forms import get_BuyForm
from ..models import *
from .index import get_list_url
from .list import HeaderMixin


class DetailView(VerifiedAccountMixin, HeaderMixin, DetailView):
    template_name = "shop/detail/default.html"
    object = None

    def get_topic(self):
        return self.get_object().name
    def get_app_index(self):
        return self.model._meta.verbose_name_plural
    def get_app_index_url(self):
        return get_list_url(self.model)
    def get_plus(self):
        return None
    def get_plus_url(self):
        return None

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        self.model = self.kwargs["model"]

    def get_queryset(self):
        return self.model.objects.prefetch_related("firma").annotate_price()

    def get_context_data(self, *args, **kwargs):
        self.object = self.object or self.get_object()

        context = super().get_context_data(*args, **kwargs)
        if not context.get("form"):
            context["form"] = get_BuyForm(self.request.spieler, self.get_object())
        
        return context


    def check_verfügbarkeit(self, form) -> bool:
        AvailableModel = apps.get_model("character", f"rel{self.model._meta.model_name}available")

        # free unused space (random, I know ...)
        AvailableModel.objects.exclude(last_tried=date.today()).delete()
        
        # how about verfügbarkeit?
        char = form.cleaned_data["char"]
        item = self.get_object()
        stufe = form.cleaned_data.get("stufe", 1)
        if not char.in_erstellung and not self.request.spieler.user.has_perm(CustomPermission.SPIELLEITUNG.value):
            
            verf = item.verfügbarkeit - (stufe - 1) * 10
            rand = random.randint(1, 100)

            # not available, try tomorrow
            if  rand > verf:
                # add mark for today's unsuccessful try
                AvailableModel.objects.create(char=char, item=item)
                return False
        return True

    def do_money_transaction(self, char: Charakter, item: BaseShop, cost: int, transaction_reason: str):
        
        # char pays money
        char.card.money -= cost
        char.card.save(update_fields=["money"])

        firma_card = None
        if not self.request.spieler.user.has_perm(CustomPermission.SPIELLEITUNG.value):
            spielleitung_spieler = get_object_or_404(Spieler, user__username__startswith="spielleit")
            firma_card = Card.objects.get_or_create(name=item.firma.name, spieler=spielleitung_spieler)[0]

            # firma receives money
            firma_card.money += cost
            firma_card.save(update_fields=["money"])

        # add Transaction
        Transaction.objects.create(sender=char.card, receiver=firma_card, amount=cost, reason=transaction_reason)
        

    
    def post(self, *args, **kwargs):
        item = self.get_object()

        form = get_BuyForm(self.request.spieler, item)(self.request.POST)
        form.full_clean()
        if not form.is_valid():
            return render(self.request, self.template_name, self.get_context_data(form=form))
    
        if not self.check_verfügbarkeit(form):
            messages.error(self.request, f"{item.name} ist zurzeit nicht verfügbar. Try again tomorrow.")
            return render(self.request, self.template_name, self.get_context_data(form=form))

        # prepare relevant fields
        char = form.cleaned_data["char"]
        amount = form.cleaned_data["amount"]
        stufe = form.cleaned_data.get("stufe")

        # pay
        cost = form.cleaned_data["amount"] * form.cleaned_data.get("price", item.curr_price or 0) * form.cleaned_data.get("stufe", 1)
        reason = f"kaufe {amount}x {item.name}{' Stufe {}'.format(stufe) if item.stufenabhängig else ''}"
        self.do_money_transaction(char, item, cost, reason)

        # add item to char
        RelShopModel = apps.get_model("character", f"rel{self.model._meta.model_name}")
        rel = RelShopModel.objects.filter(char=char, item=item, stufe=stufe).first()
        if rel is not None:
            rel.anz += amount
            rel.save(update_fields=["anz"])
        else:
            rel = RelShopModel.objects.create(char=char, item=item, stufe=stufe, anz=amount)

        # log
        logShop(self.request.spieler, char, {
            "num": amount, "item": item, "preis_ges": cost, "stufe": stufe,
            "firma_titel": item.firma.name if not self.request.spieler.user.has_perm(CustomPermission.SPIELLEITUNG.value) else "außer der Reihe"
        })

        messages.success(self.request, f"{char.name} hat {cost} Dr. für {amount}x {item.name} ausgegeben.")
        return redirect(self.request.build_absolute_uri())

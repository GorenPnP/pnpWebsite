import random
from datetime import date

from django.apps import apps
from django.core.exceptions import FieldDoesNotExist
from django.contrib import messages
from django.db.models import ManyToManyField, ManyToManyRel, ManyToOneRel
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import DetailView

from cards.models import Card, Transaction
from character.models import *
from character.permissions import CustomPermission
from log.create_log import logShop
from ppServer.mixins import VerifiedAccountMixin

from ..forms import get_BuyForm
from ..models import *
from .index import get_list_url, shopmodel_list
from .list import HeaderMixin


class DetailView(VerifiedAccountMixin, HeaderMixin, DetailView):
    template_name = "shop/detail.html"
    object = None
    context_object_name = "object"

    paginate_by = 6

    def get_topic(self):
        return self.object.name
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
        self.get_object()

    def get_queryset(self):
        qs = self.model.objects.select_related("firma").annotate_price()
        if self.model == Fernkampfwaffe:
            qs = qs.annotate_schaden()
        try:
            self.model._meta.get_field("fertigkeit")
            qs = qs.prefetch_related("fertigkeit")
        except FieldDoesNotExist:
            pass
        return qs

    def get_object(self, *args, **kwargs):
        if not self.object: self.object = get_object_or_404(self.model.objects.select_related("firma").annotate_price(), pk=self.kwargs["pk"])
        return self.object

    def get_table_fields(self):
        excluded_types = [ManyToManyRel, ManyToOneRel, ManyToManyField]
        excluded_fields = ["pk", "id", "ab_stufe", "icon", "name", "beschreibung", "frei_editierbar", "stufenabhängig", "verfügbarkeit", "firma", "price", "has_implementation"]

        field_list = []
        for field in self.model._meta.get_fields():
            if type(field) in excluded_types or field.name in excluded_fields: continue

            name = field.verbose_name or field.name
            value = getattr(self.object, f"get_{field.name}_display")() if field.choices else getattr(self.object, field.name)
            field_list.append({"name": name, "value": value})
        return field_list

    def get_firma_peers(self) -> list[BaseShop]:
        ''' get all shop items (except Tinker), filter and sort them '''

        # get filtered objects
        objects = []
        for Model in [m for m in shopmodel_list if m != Tinker]:
            qs = Model.objects.annotate_schaden() if Model == Fernkampfwaffe else Model.objects
            
            # rm self.object from result
            if Model == self.object._meta.model: qs = qs.exclude(pk=self.object.pk)

            # construct base queryset without frei_editierbare instances, apply user-filters and return objects as dicts in list
            objects += qs.annotate_price().filter(frei_editierbar=False, firma=self.object.firma)

        # sort objects randomly
        random.shuffle(objects)
        return objects[:self.paginate_by]

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(
            *args, **kwargs,
            table_fields=self.get_table_fields(),
            firma_peers=self.get_firma_peers(),
        )

        if "form" not in context: context["form"] = get_BuyForm(self.request.spieler, self.object)

        # slots & upgrades (not in every model)
        try:
            context["slots"] = getattr(self.object, f"slot{self.model._meta.model_name}_set").prefetch_related("tag").annotate(
                tag_names = ConcatSubquery(Tag.objects.filter(**{f"slot{self.model._meta.model_name}": OuterRef("pk")}).values("name")),
                num_tags = Count("tag"),
            )
        except: pass
        try:
            context["upgrades"] = self.object.possible_upgrades.select_related("tag", "prerequisite").order_by("ab_stufe", "tag__name")
        except: pass

        return context


    def check_verfügbarkeit(self, form) -> bool:
        AvailableModel = apps.get_model("character", f"rel{self.model._meta.model_name}available")

        # free unused space (random, I know ...)
        AvailableModel.objects.exclude(last_tried=date.today()).delete()
        
        # how about verfügbarkeit?
        char = form.cleaned_data["char"]
        stufe = form.cleaned_data.get("stufe", 1)
        if not char.in_erstellung and not self.request.spieler.user.has_perm(CustomPermission.SPIELLEITUNG.value):
            
            verf = self.object.verfügbarkeit - (stufe - 1) * 10
            rand = random.randint(1, 100)

            # not available, try tomorrow
            if  rand > verf:
                # add mark for today's unsuccessful try
                AvailableModel.objects.create(char=char, item=self.object)
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
        form = get_BuyForm(self.request.spieler, self.object)(self.request.POST)
        form.full_clean()
        if not form.is_valid():
            return render(self.request, self.template_name, self.get_context_data(form=form))
    
        if not self.check_verfügbarkeit(form):
            messages.error(self.request, f"{self.object.name} ist zurzeit nicht verfügbar. Try again tomorrow.")
            return render(self.request, self.template_name, self.get_context_data(form=form))

        # prepare relevant fields
        char = form.cleaned_data["char"]
        amount = form.cleaned_data["amount"]
        stufe = form.cleaned_data.get("stufe")

        # pay
        cost = form.cleaned_data["amount"] * form.cleaned_data.get("price", self.object.curr_price or 0) * form.cleaned_data.get("stufe", 1)
        reason = f"kaufe {amount}x {self.object.name}{' Stufe {}'.format(stufe) if self.object.stufenabhängig else ''}"
        self.do_money_transaction(char, self.object, cost, reason)

        # add item to char
        RelShopModel = apps.get_model("character", f"rel{self.model._meta.model_name}")
        rel = RelShopModel.objects.filter(char=char, item=self.object, stufe=stufe).first()
        if rel is not None:
            rel.anz += amount
            rel.save(update_fields=["anz"])
        else:
            rel = RelShopModel.objects.create(char=char, item=self.object, stufe=stufe, anz=amount)

        # log
        logShop(self.request.spieler, char, {
            "num": amount, "item": self.object, "preis_ges": cost, "stufe": stufe,
            "firma_titel": self.object.firma.name if not self.request.spieler.user.has_perm(CustomPermission.SPIELLEITUNG.value) else "außer der Reihe"
        })

        messages.success(self.request, f"{char.name} hat {cost} Dr. für {amount}x {self.object.name} ausgegeben.")
        return redirect(self.request.build_absolute_uri())

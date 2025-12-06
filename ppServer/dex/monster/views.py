from random import sample
from typing import Any, Dict

from django.contrib import messages
from django.db.models import Prefetch, Subquery, Max
from django.db.models.query import QuerySet
from django.http import HttpRequest, HttpResponse, HttpResponseNotFound
from django.shortcuts import get_object_or_404, reverse, redirect
from django.views.generic import DetailView
from django.views.decorators.http import require_POST
from django.views.generic.base import TemplateView
from django.views.generic.list import ListView
from django.urls import reverse

from ppServer.decorators import verified_account
from ppServer.mixins import VerifiedAccountMixin
from ppServer.utils import AvgSubquery

from .forms import *
from .models import *


class MonsterIndexView(VerifiedAccountMixin, ListView):
    model = Monster
    template_name = "dex/monster/monster_index.html"

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        return super().get_context_data(
            **kwargs,
            app_index = "Allesdex",
            app_index_url = reverse("dex:index"),
            topic = "Monsterdex",
            types = Typ.objects.all(),
            spieler = self.request.spieler.instance,
        )
    
    def get_queryset(self) -> QuerySet[Any]:
        return self.model.objects.load_card()


class MonsterDetailView(VerifiedAccountMixin, DetailView):
    model = Monster
    template_name = "dex/monster/monster_detail.html"

    def _create_form(self, **kwargs):
        if self.request.spieler.is_spielleitung:
            return SpSpielerMonsterForm(**kwargs)
        else:
            return SpielerMonsterForm(**kwargs)

    def _skill_spmo(self, instance: SpielerMonster, keep_attacks: bool):

        # create stats & get skilled
        stats = RangStat.objects.bulk_create([
            RangStat(stat=stat, spielermonster=instance)
            for (stat, _) in RangStat.StatType
        ])
        skilled_at_stat_pks = [stats[i].pk for i in sample(range(len(RangStat.StatType)), RangStat.AMOUNT_SKILLED)]
        RangStat.objects.filter(pk__in=skilled_at_stat_pks).update(skilled=True)

        # rank-up stats :)
        for _ in range(instance.rang): instance.level_up()

        # .. attackenpunkte
        instance.attackenpunkte = sum(MonsterRang.objects.filter(rang__lte=instance.rang).values_list("attackenpunkte", flat=True))
        instance.save(update_fields=["attackenpunkte"])


        # assign attacks

        # spielleitung may keep the original attacks
        attacks = instance.monster.attacken.all()
        # .. otherwise assign random attacks
        if not keep_attacks:
            free_attacks = list(instance.monster.attacken.exclude(draft=True).filter(cost=0))
            attacks = sample(free_attacks, 2) if len(free_attacks) > 2 else free_attacks

        SpielerMonsterAttack.objects.bulk_create([
            SpielerMonsterAttack(spieler_monster=instance, attacke=attack, cost=0)
            for attack in attacks
        ])

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(
            **kwargs,
            app_index = "Monster",
            app_index_url = reverse("dex:monster_index"),
            spieler = self.request.spieler.instance,
        )
        self.object = context["object"]
        context["topic"] = self.object.name
        context["form"] = self._create_form(initial={"name": self.object.name, "rang": self.object.wildrang})
        context["max_stat_wert"] = RangStat.STAT_RANG0_MAX_WERT
        context.update(self.object.get_type_efficiencies())

        return context

    def get_queryset(self) -> QuerySet[Any]:
        return self.model.objects.with_rang().prefetch_related(
            "types", "visible", "fähigkeiten",
            Prefetch("evolutionPre", Monster.objects.load_card()),
            Prefetch("evolutionPost", Monster.objects.load_card()),
            Prefetch("alternativeForms", Monster.objects.load_card()),
            Prefetch("opposites", Monster.objects.load_card()),
            Prefetch("attacken", Attacke.objects.load_card().exclude(draft=True)),
        )

    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        response = super().get(request, *args, **kwargs)    # let self.get_context_data() set self.object to perform the query only once

        spieler = self.request.spieler.instance
        if not self.object.visible.filter(id=spieler.id).exists():
            return redirect("dex:monster_index")

        return response

    def post(self, request, **kwargs):
        spieler = self.request.spieler.instance
        monster = self.get_object()
        if not monster.visible.filter(id=spieler.id).exists():
            messages.error(request, "Huch! Das Monster kennst du noch gar nicht.")
            return redirect(request.build_absolute_uri())

        form = self._create_form(data=request.POST)
        form.full_clean()
        if form.is_valid():

            # catch monster
            obj = form.save(commit=False)
            obj.monster = monster
            obj.spieler = spieler
            if obj.name == monster.name: obj.name = None
            obj.save()
            self._skill_spmo(obj, self.request.spieler.is_spielleitung and "keep_attacks" in form.cleaned_data and form.cleaned_data["keep_attacks"])

            messages.success(request, format_html(f"<b>{obj.name or monster.name}</b> ist in deiner <a class='text-light' href='{reverse('dex:monster_farm')}'>Monster-Farm</a> eingetroffen."))
        else:
            messages.error(request, "Etwas ist schief gelaufen. Das Monster konnte nicht gefangen werden.")
        return redirect(request.build_absolute_uri())
    
class AttackIndexView(VerifiedAccountMixin, ListView):
    model = Attacke
    template_name = "dex/monster/attack_index.html"

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        return super().get_context_data(
            **kwargs,
            app_index = "Allesdex",
            app_index_url = reverse("dex:index"),
            topic = "Attacken",
            types = Typ.objects.all(),
            all_stats = [(stat, label) for stat, label in RangStat.StatType if stat in ["N", "F", "MA", "VER_G", "VER_K"]]
        )
    
    def get_queryset(self) -> QuerySet[Any]:
        return self.model.objects.load_card().exclude(draft=True)


class TypeTableView(VerifiedAccountMixin, ListView):
    model = Typ
    template_name = "dex/monster/type_table.html"

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        return super().get_context_data(
            **kwargs,
            app_index = "Allesdex",
            app_index_url = reverse("dex:index"),
            topic = "Typentabelle"
        )
    
    def get_queryset(self) -> QuerySet[Any]:
        return super().get_queryset().prefetch_related("stark_gegen", "schwach_gegen", "trifft_nicht", "stark", "schwach", "miss")


class MonsterFähigkeitView(VerifiedAccountMixin, ListView):
    model = MonsterFähigkeit
    template_name = "dex/monster/monster_fähigkeit_index.html"

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        return super().get_context_data(
            **kwargs,
            app_index = "Allesdex",
            app_index_url = reverse("dex:index"),
            topic = "Fähigkeiten",
            spieler = self.request.spieler.instance,
        )

    def get_queryset(self) -> QuerySet[Any]:
        return super().get_queryset().prefetch_related(Prefetch("monster_set", queryset=Monster.objects.load_card()))


class StatusEffektView(VerifiedAccountMixin, TemplateView):
    template_name = "dex/monster/monster_statuseffekt.html"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        return super().get_context_data(
            **kwargs,
            app_index = "Allesdex",
            app_index_url = reverse("dex:index"),
            topic="Status-Effekte"
        )


class MonsterFarmView(VerifiedAccountMixin, ListView):
    model = SpielerMonster
    template_name = "dex/monster/monster_farm.html"

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        return super().get_context_data(
            **kwargs,
            app_index = "Allesdex",
            app_index_url = reverse("dex:index"),
            topic = "Monster-Farm",
            types = Typ.objects.all(),
            spieler = self.request.spieler.instance,
        )
    
    def get_queryset(self) -> QuerySet[Any]:
        return super().get_queryset()\
            .prefetch_related(Prefetch("monster", Monster.objects.load_card()))\
            .filter(spieler=self.request.spieler.instance)


class MonsterFarmDetailView(VerifiedAccountMixin, DetailView):
    model = SpielerMonster
    template_name = "dex/monster/monster_farm_detail.html"

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(
            **kwargs,
            app_index = "Farm",
            app_index_url = reverse("dex:monster_farm"),
            spieler = self.request.spieler.instance,
            types = Typ.objects.all(),
            all_stats = [(stat, label) for stat, label in RangStat.StatType if stat in ["N", "F", "MA", "VER_G", "VER_K"]],
        )
        self.object = context["object"]
        context["topic"] = self.object.name or self.object.monster.name
        context["form"] = SpielerMonsterNameForm(instance=context["object"])
        context["other_attacks"] = self.object.get_buyable_attacks().prefetch_related("damage")
        
        context["other_teams"] = MonsterTeam.objects.filter(spieler=context["spieler"]).exclude(monster=self.object)
        context["monster"] = Monster.objects.with_rang().prefetch_related(
            "types", "visible", "fähigkeiten",
            Prefetch("evolutionPre", Monster.objects.load_card()),
            Prefetch("evolutionPost", Monster.objects.load_card()),
            Prefetch("alternativeForms", Monster.objects.load_card()),
            Prefetch("opposites", Monster.objects.load_card()),
        ).get(id=context["object"].monster.id)
        context["max_stat_wert"] = max(self.object.initiative, self.object.hp, self.object.nahkampf, self.object.fernkampf, self.object.magie, self.object.verteidigung_geistig, self.object.verteidigung_körperlich)
        context["schadensWI"] = Dice.toString(
            *context["monster"].base_schadensWI_str.split(" + "),
            *context["object"].rang_schadensWI_str.split(" + ")
        )
        context["WEIGHT_SKILLED"] = RangStat.WEIGHT_SKILLED
        context["WEIGHT_TRAINED"] = RangStat.WEIGHT_TRAINED
        context["AMOUNT_TRAINED"] = RangStat.AMOUNT_TRAINED
        context["MAX_AMOUNT_ATTACKEN"] = SpielerMonster.MAX_AMOUNT_ATTACKEN

        return context

    def get_queryset(self) -> QuerySet[Any]:
        return self.model.objects.with_rang_and_stats().prefetch_related(
            Prefetch("spielermonsterattack_set__attacke", queryset=Attacke.objects.load_card())
        )
        
    def get(self, request: HttpRequest, pk: int, *args: Any, **kwargs: Any) -> HttpResponse:
        response = super().get(request, *args, **kwargs)    # let self.get_context_data() set self.object to perform the query only once
        
        # authorization
        spieler = self.request.spieler.instance
        get_object_or_404(self.model, spieler=spieler, pk=pk)
        if not self.object.monster.visible.filter(id=spieler.id).exists():
            return redirect("dex:monster_farm")

        return response
    
    def post(self, request, pk: int, *args, **kwargs):
        # authorization
        spieler = self.request.spieler.instance
        object = get_object_or_404(self.model, spieler=spieler, pk=pk)
        if not object.monster.visible.filter(id=spieler.id).exists():
            return redirect("dex:monster_farm")

        # work
        form = SpielerMonsterNameForm(request.POST, instance=self.get_object())
        form.full_clean()
        if form.is_valid():
            obj = form.save()
            if obj.name == obj.monster.name:
                obj.name = None
                obj.save(update_fields=["name"])
            messages.success(request, "Änderungen erfolgreich gespeichert")
        else:
            messages.error(request, "Ein Fehler ist aufgetreten, die Änderungen wurden nicht gespeichert")
        return redirect(request.build_absolute_uri())


class MonsterFarmLevelupView(VerifiedAccountMixin, DetailView):
    """
        display:
          reaktionsbonus, attackbonus, schadensWI
        calc:
          7 stats of Monsterart
        calc & save:
          random polls of stats, attackenpunkte
    """

    model = SpielerMonster
    template_name = "dex/monster/monster_farm_levelup.html"

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(
            **kwargs,
            app_index = "Farm",
            app_index_url = reverse("dex:monster_farm"),
            spieler = self.request.spieler.instance,
        )
        self.object = context["object"]
        context["topic"] = (self.object.name or self.object.monster.name) + " - Level up"
        context["max_stat_wert"] = max(self.object.initiative, self.object.hp, self.object.nahkampf, self.object.fernkampf, self.object.magie, self.object.verteidigung_geistig, self.object.verteidigung_körperlich)
        context["new_rang"] = MonsterRang.objects.prefetch_related("schadensWI").filter(rang=self.object.rang+1).first()

        # stats & stat calculation values for js
        context["all_stats"] = [stat for stat, _ in RangStat.StatType]
        context["POLLS_PER_RANG"] = RangStat.POLLS_PER_RANG
        context["WEIGHT_BASE"] = RangStat.WEIGHT_BASE
        context["WEIGHT_SKILLED"] = RangStat.WEIGHT_SKILLED
        context["WEIGHT_TRAINED"] = RangStat.WEIGHT_TRAINED

        # schadensWI
        base_schadensWI = [d.__str__() for d in self.object.monster.base_schadensWI.all()]
        context["schadensWI"] = Dice.toString(
            *base_schadensWI,
            *self.object.rang_schadensWI_str.split(" + ")
        )
        if context["new_rang"]:
            context["new_schadensWI"] = Dice.toString(
                *base_schadensWI,
                *[d.__str__() for d in context["new_rang"].schadensWI.all()],
            )
        else: 
            context["new_schadensWI"] = context["schadensWI"]

        return context

    def get_queryset(self) -> QuerySet[Any]:
        stat_qs = RangStat.objects.filter(spielermonster__id=OuterRef("id"))

        return self.model.objects.with_rang_and_stats().annotate(
            new_rang_faktor = 1.0 * (F("rang")+1 + SpielerMonster.ARTSPEZIFISCHER_RANGFAKTOR) / SpielerMonster.ARTSPEZIFISCHER_RANGFAKTOR,

            new_initiative = Cast(F("monster__base_initiative") * F("new_rang_faktor") + Subquery(stat_qs.filter(stat="INI").values("wert")[:1]), output_field=models.IntegerField()),
            new_hp = Cast(F("monster__base_hp") * F("new_rang_faktor") + Subquery(stat_qs.filter(stat="HP").values("wert")[:1]), output_field=models.IntegerField()),
            new_nahkampf = Cast(F("monster__base_nahkampf") * F("new_rang_faktor") + Subquery(stat_qs.filter(stat="N").values("wert")[:1]), output_field=models.IntegerField()),
            new_fernkampf = Cast(F("monster__base_fernkampf") * F("new_rang_faktor") + Subquery(stat_qs.filter(stat="F").values("wert")[:1]), output_field=models.IntegerField()),
            new_magie = Cast(F("monster__base_magie") * F("new_rang_faktor") + Subquery(stat_qs.filter(stat="MA").values("wert")[:1]), output_field=models.IntegerField()),
            new_verteidigung_geistig = Cast(F("monster__base_verteidigung_geistig") * F("new_rang_faktor") + Subquery(stat_qs.filter(stat="VER_G").values("wert")[:1]), output_field=models.IntegerField()),
            new_verteidigung_körperlich = Cast(F("monster__base_verteidigung_körperlich") * F("new_rang_faktor") + Subquery(stat_qs.filter(stat="VER_K").values("wert")[:1]), output_field=models.IntegerField()),

        )
        
    def get(self, request: HttpRequest, pk: int,  *args: Any, **kwargs: Any) -> HttpResponse:
        response = super().get(request, *args, **kwargs)    # let self.get_context_data() set self.object to perform the query only once

        # authorization
        spieler = self.request.spieler.instance
        get_object_or_404(self.model, spieler=spieler, pk=pk)
        if not self.object.monster.visible.filter(id=spieler.id).exists():
            return redirect("dex:monster_farm")
        
        if self.object.rangstat_set.filter(trained=True).count() != RangStat.AMOUNT_TRAINED:
            messages.error(request, f"Du musst {RangStat.AMOUNT_TRAINED} Stats trainieren, bevor das Monster im Rang steigen kann")
            return redirect(reverse("dex:monster_detail_farm", args=[pk]))

        return response
    
    def post(self, request, pk: int, *args, **kwargs):
        # authorization
        spieler = request.spieler.instance
        object = get_object_or_404(self.model, spieler=spieler, pk=pk)
        if not object.monster.visible.filter(id=spieler.id).exists():
            return redirect("dex:monster_farm")
        
        if object.rangstat_set.filter(trained=True).count() != RangStat.AMOUNT_TRAINED:
            messages.error(request, f"Du musst {RangStat.AMOUNT_TRAINED} Stats trainieren, bevor das Monster im Rang steigen kann")
            return redirect(reverse("dex:monster_detail_farm", args=[pk]))

        # work
        all_stats = [stat for stat, _ in RangStat.StatType]
        stats = set([key for key in request.POST.keys() if key in all_stats])
        if len(stats) != RangStat.POLLS_PER_RANG:
            messages.error(request, f"Es sind nicht {RangStat.POLLS_PER_RANG} Stats ausgewählt worden")
            return redirect(request.build_absolute_uri())
        
        # stats
        db_stats = []
        for stat in object.rangstat_set.filter(stat__in=stats):
            stat.wert += 1
            db_stats.append(stat)
        RangStat.objects.bulk_update(db_stats, fields=["wert"])

        # attackenpunkte
        new_rang = MonsterRang.objects.filter(rang=object.rang+1).first()
        if new_rang and new_rang.attackenpunkte:
            object.attackenpunkte += new_rang.attackenpunkte
            object.save(update_fields=["attackenpunkte"])

        # rang
        object.rang += 1
        object.save(update_fields=["rang"])

        messages.success(request, "Levelup erfolgreich gespeichert")
        return redirect(reverse("dex:monster_detail_farm", args=[pk]))



class MonsterTeamView(VerifiedAccountMixin, ListView):
    model = MonsterTeam
    template_name = "dex/monster/monster_teams.html"

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(
            **kwargs,
            app_index = "Allesdex",
            app_index_url = reverse("dex:index"),
            topic = "Monster-Teams",
            spieler = self.request.spieler.instance,
            form = TeamForm()
        )

        # max for stat display
        context["max_stat_wert"] = max(1, *context["object_list"].aggregate(
            Max("stat_initiative"),
            Max("stat_hp"),
            Max("stat_nahkampf"),
            Max("stat_fernkampf"),
            Max("stat_magie"),
            Max("stat_verteidigung_geistig"),
            Max("stat_verteidigung_körperlich"),
        ).values()) if context["object_list"].count() else 1

        return context

    def get_queryset(self) -> QuerySet[Any]:
        monster_stat_qs = SpielerMonster.objects.with_rang_and_stats().filter(monsterteam=OuterRef("pk"))

        return super().get_queryset()\
            .prefetch_related(
                Prefetch("monster__monster", Monster.objects.load_card()),
                "monster__monster__attacken__types"
            )\
            .filter(spieler=self.request.spieler.instance)\
            .annotate(

                # stats
                rang = Coalesce(AvgSubquery(monster_stat_qs, "rang_rang"), 0),
                stat_initiative = Coalesce(AvgSubquery(monster_stat_qs, "initiative"), 0),
                stat_hp = Coalesce(AvgSubquery(monster_stat_qs, "hp"), 0),
                stat_nahkampf = Coalesce(AvgSubquery(monster_stat_qs, "nahkampf"), 0),
                stat_fernkampf = Coalesce(AvgSubquery(monster_stat_qs, "fernkampf"), 0),
                stat_magie = Coalesce(AvgSubquery(monster_stat_qs, "magie"), 0),
                stat_verteidigung_geistig = Coalesce(AvgSubquery(monster_stat_qs, "verteidigung_geistig"), 0),
                stat_verteidigung_körperlich = Coalesce(AvgSubquery(monster_stat_qs, "verteidigung_körperlich"), 0),
            )
    
    def post(self, request, **kwargs):
        spieler = request.spieler.instance
        form = TeamForm(request.POST)
        form.full_clean()
        if form.is_valid():
            obj = MonsterTeam.objects.create(**form.cleaned_data, spieler=spieler)

            messages.success(request, "Neues Team erstellt")
            return redirect(reverse("dex:monster_team_detail", args=[obj.id]))
        messages.error(request, "Ein Fehler ist aufgetreten. Das Team konnte nicht erstellt werden.")
        return redirect(request.build_absolute_uri())


class MonsterTeamDetailView(VerifiedAccountMixin, DetailView):
    model = MonsterTeam
    template_name = "dex/monster/monster_teams_detail.html"

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(
            **kwargs,
            app_index = "Monster-Teams",
            app_index_url = reverse("dex:monster_team"),
            spieler = self.request.spieler.instance,
        )
        context["topic"] = context["object"].name
        context["own_monsters"] = SpielerMonster.objects.filter(spieler=context["spieler"]).exclude(id__in=context["object"].monster.values_list("id", flat=True))
        context["form"] = TeamForm(initial={
            "name": context["object"].name,
            "farbe": context["object"].farbe,
            "textfarbe": context["object"].textfarbe
        })
        return context

    def get_queryset(self) -> QuerySet[Any]:
        return super().get_queryset()\
            .prefetch_related("monster")\
            .filter(spieler=self.request.spieler.instance)
    
    def post(self, request, **kwargs):
        form = TeamForm(request.POST)
        form.full_clean()
        if form.is_valid():
            obj = self.get_object()
            obj.name = form.cleaned_data["name"]
            obj.farbe = form.cleaned_data["farbe"]
            obj.textfarbe = form.cleaned_data["textfarbe"]
            obj.save(update_fields=["name", "farbe", "textfarbe"])
            messages.success(request, "Änderungen erfolgreich gespeichert")
        else:
            messages.error(request, "Ein Fehler ist aufgetreten, die Änderungen wurden nicht gespeichert")

        return redirect(request.build_absolute_uri())


@require_POST
@verified_account
def add_monster_to_team(request, pk):
    team = get_object_or_404(MonsterTeam, pk=pk, spieler=request.spieler.instance)
    monster = get_object_or_404(SpielerMonster, pk=request.POST.get("monster_id"), spieler=request.spieler.instance)
    team.monster.add(monster)
    messages.success(request, f"{monster.name or monster.monster.name} ist {team.name} beigetreten")
    
    redirect_path = request.GET.get("redirect")
    return redirect(redirect_path if redirect_path and redirect_path.startswith("/dex/") else reverse("dex:monster_team_detail", args=[pk]))

@require_POST
@verified_account
def delete_monster_from_team(request, pk):
    team = get_object_or_404(MonsterTeam, pk=pk, spieler=request.spieler.instance)
    monster = get_object_or_404(SpielerMonster, pk=request.POST.get("monster_id"))
    team.monster.remove(monster)
    messages.success(request, f"{monster.name or monster.monster.name} ist aus {team.name} ausgetreten")

    redirect_path = request.GET.get("redirect")
    return redirect(redirect_path if redirect_path and redirect_path.startswith("/dex/") else reverse("dex:monster_team_detail", args=[pk]))

@require_POST
@verified_account
def add_team_to_spielermonster(request, pk):
    sp_mo = get_object_or_404(SpielerMonster, pk=pk, spieler=request.spieler.instance)
    team = get_object_or_404(MonsterTeam, pk=request.POST.get("team_id"))
    sp_mo.monsterteam_set.add(team)
    messages.success(request, f"{sp_mo.name or sp_mo.monster.name} ist {team.name} beigetreten")

    redirect_path = request.GET.get("redirect")
    return redirect(redirect_path if redirect_path and redirect_path.startswith("/dex/") else reverse("dex:monster_detail_farm", args=[pk]))

@require_POST
@verified_account
def delete_spielermonster(request):
    sp_mo = get_object_or_404(SpielerMonster, pk=request.POST.get("monster_id"), spieler=request.spieler.instance)
    SpielerMonster.objects.filter(pk=sp_mo.pk).delete()

    messages.success(request, format_html(f"{sp_mo.name or sp_mo.monster.name} ist frei!"))

    redirect_path = request.GET.get("redirect")
    return redirect(redirect_path if redirect_path and redirect_path.startswith("/dex/") else reverse("dex:monster_farm"))

@require_POST
@verified_account
def set_training_of_spielermonster(request, pk):
    sp_mo = get_object_or_404(SpielerMonster, pk=pk, spieler=request.spieler.instance)
    all_stats = [stat for stat, _ in RangStat.StatType]
    stats = [stat.strip() for stat in request.POST.get("stat").split(" ")]
    stats = set([stat for stat in stats if stat in all_stats])
    if len(stats) != RangStat.AMOUNT_TRAINED:
        messages.error(request, f"{sp_mo.name or sp_mo.monster.name} hat nicht genau {RangStat.AMOUNT_TRAINED} trainierte Stats!")

    else:
        db_stats = []
        for rang_stat in RangStat.objects.filter(spielermonster=sp_mo):
            rang_stat.trained = rang_stat.stat in stats
            db_stats.append(rang_stat)
        RangStat.objects.bulk_update(db_stats, fields=["trained"])

        lables = [f"<b>{label}</b>" for stat, label in RangStat.StatType if stat in stats]
        lable_str = " und ".join([", ".join(lables[:-1]), lables[-1]])
        messages.success(request, format_html(f"{sp_mo.name or sp_mo.monster.name} trainiert nun {lable_str}!"))

    redirect_path = request.GET.get("redirect")
    return redirect(redirect_path if redirect_path and redirect_path.startswith("/dex/") else reverse("dex:monster_detail_farm", args=[pk]))

@require_POST
@verified_account
def add_attack_to_spielermonster(request, pk):
    sp_mo = get_object_or_404(SpielerMonster, pk=pk, spieler=request.spieler.instance)

    attack = None
    try:
        attack = sp_mo.get_buyable_attacks().get(pk=request.POST.get("attack_id"))
    except: pass

    if attack is None:
        messages.error(request, f"{sp_mo.name or sp_mo.monster.name} kann diese Attacke nicht lernen.")

    elif sp_mo.attacken.count() >= SpielerMonster.MAX_AMOUNT_ATTACKEN:
        messages.error(request, f"{sp_mo.name or sp_mo.monster.name} kennt schon zu viele Attacken. Vegesse eine Andere, um diese hier zu erlernen.")

    else:
        SpielerMonsterAttack.objects.create(spieler_monster=sp_mo, attacke=attack, cost=attack.modified_cost)

        sp_mo.attackenpunkte -= attack.modified_cost
        sp_mo.save(update_fields=["attackenpunkte"])

        messages.success(request, format_html(f"{sp_mo.name or sp_mo.monster.name} hat <b>{attack.name} gelernt</b>"))

    redirect_path = request.GET.get("redirect")
    return redirect(redirect_path if redirect_path and redirect_path.startswith("/dex/") else reverse("dex:monster_detail_farm", args=[pk]))

@require_POST
@verified_account
def delete_attack_from_spielermonster(request, pk):

    # get stuff
    sp_mo = get_object_or_404(SpielerMonster, pk=pk, spieler=request.spieler.instance)
    sp_mo_attack = get_object_or_404(SpielerMonsterAttack, spieler_monster=sp_mo, attacke__id=request.POST.get("attack_id"))
    
    # remove attack
    SpielerMonsterAttack.objects.filter(id=sp_mo_attack.id).delete()

    # add attackenpunkte
    sp_mo.attackenpunkte += sp_mo_attack.cost
    sp_mo.save(update_fields=["attackenpunkte"])

    messages.success(request, format_html(f"{sp_mo.name or sp_mo.monster.name} hat <b>{sp_mo_attack.attacke.name} verlernt</b>"))
    redirect_path = request.GET.get("redirect")
    return redirect(redirect_path if redirect_path and redirect_path.startswith("/dex/") else reverse("dex:monster_detail_farm", args=[pk]))


@require_POST
@verified_account
def evolve_spielermonster(request, pk):

    # get stuff
    sp_mo = get_object_or_404(SpielerMonster, pk=pk, spieler=request.spieler.instance)
    monster = get_object_or_404(Monster, pk=request.POST.get("monster_id"))
    
    # check valid evolution?
    if not sp_mo.monster.evolutionPre.filter(id=monster.id).exists() and not sp_mo.monster.evolutionPost.filter(id=monster.id).exists():
        messages.error(request, f"{monster.name} ist keine Entwicklung von deinem {sp_mo.name or sp_mo.monster.name}")
    else:
        name = sp_mo.name or sp_mo.monster.name

        # evolve
        sp_mo.monster = monster
        sp_mo.save(update_fields=["monster"])

        # mark monster as visible (could be previously unknown to the Spieler)
        monster.visible.add(sp_mo.spieler.id)

        messages.success(request, format_html(f"{name} hat sich <b>in {monster.name} entwickelt</b>!"))
    
    redirect_path = request.GET.get("redirect")
    return redirect(redirect_path if redirect_path and redirect_path.startswith("/dex/") else reverse("dex:monster_detail_farm", args=[pk]))


class AttackProposalView(VerifiedAccountMixin, ListView):
    model = Attacke
    template_name = "dex/monster/attack_proposal.html"

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(
            **kwargs,
            app_index = "Allesdex",
            app_index_url = reverse("dex:index"),
            topic = "Attacken-Vorschlag",
            is_create = "pk" not in self.kwargs,
            form = ProposeAttackForm(),

            types=Typ.objects.all(),
            all_stats=[(stat, label) for stat, label in RangStat.StatType if stat in ["N", "F", "MA", "VER_G", "VER_K"]],
        )
        if not context["is_create"]:
            spieler = self.request.spieler.instance
            if not spieler: HttpResponseNotFound()

            obj = get_object_or_404(Attacke, pk=self.kwargs["pk"], author=spieler, draft=True)
            context["form"] = ProposeAttackForm(instance=obj)

        return context
    
    def get_queryset(self) -> QuerySet[Any]:
        spieler = self.request.spieler.instance
        return self.model.objects.load_card().filter(author=spieler, draft=True)

    def post(self, request, pk: int = None, *args, **kwargs):
        spieler = request.spieler.instance
        if pk is not None:
            obj = get_object_or_404(Attacke, pk=pk, author=spieler)
            form = ProposeAttackForm(request.POST, instance=obj)
        else:
            form = ProposeAttackForm(request.POST)

        form.full_clean()
        if form.is_valid():

            obj = form.save(commit=False)
            obj.author = spieler
            obj.draft = True
            obj.save()
            obj.damage.add(*form.cleaned_data["damage"].values_list("id", flat=True))
            obj.types.add(*form.cleaned_data["types"].values_list("id", flat=True))

            messages.success(request, f"{obj.name} ist {'bearbeitet' if pk is not None else 'angelegt'} worden")
        else:
            print(form.errors)
            if "types" in form.cleaned_data and form.cleaned_data["types"].count():
                messages.error(request, "Es ist ein Problem aufgetreten, die Attacke konnte nicht gespeichert werden")
            else:
                messages.error(request, "Kein Typ eingetragen")
        return redirect("dex:attack_proposal")
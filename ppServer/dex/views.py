from typing import Any, Dict

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Prefetch
from django.db.models.query import QuerySet
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, reverse, redirect
from django.views.generic import DetailView
from django.views.decorators.http import require_POST
from django.views.generic.list import ListView
from django.urls import reverse

from .forms import *
from .models import *

class MonsterIndexView(LoginRequiredMixin, ListView):
    model = Monster
    template_name = "dex/monster_index.html"

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        return super().get_context_data(
            **kwargs,
            app_index = "Allesdex",
            app_index_url = reverse("dex:index"),
            topic = "Monsterdex",
            types = Typ.objects.all(),
            spieler = get_object_or_404(Spieler, name=self.request.user.username)
        )
    
    def get_queryset(self) -> QuerySet[Any]:
        return self.model.objects.load_card()


class MonsterDetailView(LoginRequiredMixin, DetailView):
    model = Monster
    template_name = "dex/monster_detail.html"

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(
            **kwargs,
            app_index = "Monster",
            app_index_url = reverse("dex:monster_index"),
            spieler = get_object_or_404(Spieler, name=self.request.user.username)
        )
        self.object = context["object"]
        context["topic"] = self.object.name
        context["form"] = SpielerMonsterForm(initial={"name": self.object.name, "rang": self.object.wildrang})
        context["max_stat_wert"] = max(self.object.base_initiative, self.object.base_hp, self.object.base_nahkampf, self.object.base_fernkampf, self.object.base_magie, self.object.base_verteidigung_geistig, self.object.base_verteidigung_körperlich)

        return context

    def get_queryset(self) -> QuerySet[Any]:
        return self.model.objects.with_rang().prefetch_related(
            "types", "visible", "fähigkeiten",
            Prefetch("evolutionPre", Monster.objects.load_card()),
            Prefetch("evolutionPost", Monster.objects.load_card()),
            Prefetch("alternativeForms", Monster.objects.load_card()),
            Prefetch("opposites", Monster.objects.load_card()),
            Prefetch("attacken", Attacke.objects.load_card()),
        )
        
    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        response = super().get(request, *args, **kwargs)    # let self.get_context_data() set self.object to perform the query only once
        
        spieler = get_object_or_404(Spieler, name=self.request.user.username)
        if  not self.object.visible.filter(name=spieler.name).exists():
            return redirect("dex:monster_index")

        return response
    
    def post(self, request, **kwargs):
        spieler = get_object_or_404(Spieler, name=self.request.user.username)
        monster = self.get_object()
        if not monster.visible.filter(id=spieler.id).exists():
            messages.error(request, "Huch! Das Monster kennst du noch gar nicht.")
            return redirect(request.build_absolute_uri())

        form = SpielerMonsterForm(request.POST)
        form.full_clean()
        if form.is_valid():
            obj = form.save(commit=False)
            obj.monster = monster
            obj.spieler = spieler
            if obj.name == monster.name: obj.name = None
            obj.save()
            obj.attacken.add(*list(obj.monster.attacken.all().values_list("id", flat=True)))
            messages.success(request, format_html(f"{obj.name or monster.name} ist in deiner <a class='text-light' href='{reverse('dex:monster_farm')}'>Monster-Farm</a> eingetroffen."))
        else:
            messages.error(request, "Etwas ist schief gelaufen. Das Monster konnte nicht gefangen werden.")
        return redirect(request.build_absolute_uri())
    
class AttackIndexView(LoginRequiredMixin, ListView):
    model = Attacke
    template_name = "dex/attack_index.html"

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        return super().get_context_data(
            **kwargs,
            app_index = "Allesdex",
            app_index_url = reverse("dex:index"),
            topic = "Attacken",
            types = Typ.objects.all()
        )
    
    def get_queryset(self) -> QuerySet[Any]:
        return self.model.objects.load_card()


class TypeTableView(LoginRequiredMixin, ListView):
    model = Typ
    template_name = "dex/type_table.html"

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        return super().get_context_data(
            **kwargs,
            app_index = "Allesdex",
            app_index_url = reverse("dex:index"),
            topic = "Typentabelle"
        )
    
    def get_queryset(self) -> QuerySet[Any]:
        return super().get_queryset().prefetch_related("stark_gegen", "schwach_gegen", "trifft_nicht", "stark", "schwach", "miss")


class MonsterFähigkeitView(LoginRequiredMixin, ListView):
    model = MonsterFähigkeit
    template_name = "dex/monster_fähigkeit_index.html"

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        return super().get_context_data(
            **kwargs,
            app_index = "Allesdex",
            app_index_url = reverse("dex:index"),
            topic = "Fähigkeiten",
            spieler = get_object_or_404(Spieler, name=self.request.user.username),
        )

    def get_queryset(self) -> QuerySet[Any]:
        return super().get_queryset().prefetch_related(Prefetch("monster_set", queryset=Monster.objects.load_card()))


class MonsterFarmView(LoginRequiredMixin, ListView):
    model = SpielerMonster
    template_name = "dex/monster_farm.html"

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(
            **kwargs,
            app_index = "Allesdex",
            app_index_url = reverse("dex:index"),
            topic = "Monster-Farm",
            types = Typ.objects.all(),
            spieler = get_object_or_404(Spieler, name=self.request.user.username)
        )
        context["form"] = CatchMonsterForm(curr_spieler=context["spieler"])
        return context
    
    def get_queryset(self) -> QuerySet[Any]:
        return super().get_queryset()\
            .prefetch_related(Prefetch("monster", Monster.objects.load_card()))\
            .filter(spieler__name=self.request.user.username)
    
    def post(self, request, **kwargs):
        spieler = get_object_or_404(Spieler, name=self.request.user.username)
        form = CatchMonsterForm(request.POST, curr_spieler=spieler)
        form.full_clean()
        if form.is_valid():
            obj = form.save(commit=False)
            obj.spieler = spieler
            obj.save()
            obj.attacken.add(*list(obj.monster.attacken.all().values_list("id", flat=True)))
            messages.success(request, f"{obj.name or obj.monster.name} ist in deiner Monster-Farm eingetroffen.")
        else:
            messages.error(request, "Etwas ist schief gelaufen. Das Monster konnte nicht gefangen werden.")
        return redirect(request.build_absolute_uri())


class MonsterFarmDetailView(LoginRequiredMixin, DetailView):
    model = SpielerMonster
    template_name = "dex/monster_farm_detail.html"

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(
            **kwargs,
            app_index = "Farm",
            app_index_url = reverse("dex:monster_farm"),
            spieler = get_object_or_404(Spieler, name=self.request.user.username)
        )
        self.object = context["object"]
        context["topic"] = self.object.name or self.object.monster.name
        context["form"] = SpielerMonsterNameForm(instance=context["object"])
        context["other_attacks"] = Attacke.objects.exclude(spielermonster=self.object)
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

        return context

    def get_queryset(self) -> QuerySet[Any]:
        return self.model.objects.with_rang_and_stats().prefetch_related(
            Prefetch("attacken", queryset=Attacke.objects.load_card())
        )
        
    def get(self, request: HttpRequest, pk: int, *args: Any, **kwargs: Any) -> HttpResponse:
        response = super().get(request, *args, **kwargs)    # let self.get_context_data() set self.object to perform the query only once
        
        # authorization
        spieler = get_object_or_404(Spieler, name=self.request.user.username)
        get_object_or_404(self.model, spieler=spieler, pk=pk)
        if  not self.object.monster.visible.filter(name=spieler.name).exists():
            return redirect("dex:monster_farm")

        return response
    
    def post(self, request, pk: int, *args, **kwargs):
        # authorization
        spieler = get_object_or_404(Spieler, name=self.request.user.username)
        object = get_object_or_404(self.model, spieler=spieler, pk=pk)
        if not object.monster.visible.filter(name=spieler.name).exists():
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


class MonsterFarmLevelupView(LoginRequiredMixin, DetailView):
    """
        display:
          reaktionsbonus, attackbonus, schadensWI
        calc:
          7 stats of Monsterart
        calc & save:
          random polls of stats, attackenpunkte
    """

    model = SpielerMonster
    template_name = "dex/monster_farm_levelup.html"

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(
            **kwargs,
            app_index = "Farm",
            app_index_url = reverse("dex:monster_farm"),
            spieler = get_object_or_404(Spieler, name=self.request.user.username)
        )
        self.object = context["object"]
        context["topic"] = (self.object.name or self.object.monster.name) + " - Level up"
        context["max_stat_wert"] = max(self.object.initiative, self.object.hp, self.object.nahkampf, self.object.fernkampf, self.object.magie, self.object.verteidigung_geistig, self.object.verteidigung_körperlich)
        context["new_rang"] = MonsterRang.objects.filter(rang=self.object.rang+1).first()

        context["all_stats"] = [stat for stat, _ in RangStat.StatType]
        context["POLLS_PER_RANG"] = RangStat.POLLS_PER_RANG
        context["WEIGHT_BASE"] = RangStat.WEIGHT_BASE
        context["WEIGHT_SKILLED"] = RangStat.WEIGHT_SKILLED
        context["WEIGHT_TRAINED"] = RangStat.WEIGHT_TRAINED

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
        spieler = get_object_or_404(Spieler, name=self.request.user.username)
        get_object_or_404(self.model, spieler=spieler, pk=pk)
        if not self.object.monster.visible.filter(name=spieler.name).exists():
            return redirect("dex:monster_farm")

        return response
    
    def post(self, request, pk: int, *args, **kwargs):
        # authorization
        spieler = get_object_or_404(Spieler, name=self.request.user.username)
        object = get_object_or_404(self.model, spieler=spieler, pk=pk)
        if not object.monster.visible.filter(name=spieler.name).exists():
            return redirect("dex:monster_farm")

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



class MonsterTeamView(LoginRequiredMixin, ListView):
    model = MonsterTeam
    template_name = "dex/monster_teams.html"

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        return super().get_context_data(
            **kwargs,
            app_index = "Allesdex",
            app_index_url = reverse("dex:index"),
            topic = "Monster-Teams",
            spieler = get_object_or_404(Spieler, name=self.request.user.username),
            form = TeamForm()
        )

    def get_queryset(self) -> QuerySet[Any]:
        return super().get_queryset()\
            .prefetch_related(Prefetch("monster__monster", Monster.objects.load_card()))\
            .filter(spieler__name=self.request.user.username)
    
    def post(self, request, **kwargs):
        spieler = get_object_or_404(Spieler, name=request.user.username)
        form = TeamForm(request.POST)
        form.full_clean()
        if form.is_valid():
            obj = MonsterTeam.objects.create(**form.cleaned_data, spieler=spieler)

            messages.success(request, "Neues Team erstellt")
            return redirect(reverse("dex:monster_team_detail", args=[obj.id]))
        messages.error(request, "Ein Fehler ist aufgetreten. Das Team konnte nicht erstellt werden.")
        return redirect(request.build_absolute_uri())


class MonsterTeamDetailView(LoginRequiredMixin, DetailView):
    model = MonsterTeam
    template_name = "dex/monster_teams_detail.html"

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(
            **kwargs,
            app_index = "Monster-Teams",
            app_index_url = reverse("dex:monster_team"),
            spieler = get_object_or_404(Spieler, name=self.request.user.username)
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
            .filter(spieler__name=self.request.user.username)
    
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
@login_required
def add_monster_to_team(request, pk):
    team = get_object_or_404(MonsterTeam, pk=pk, spieler__name=request.user.username)
    monster = get_object_or_404(SpielerMonster, pk=request.POST.get("monster_id"), spieler__name=request.user.username)
    team.monster.add(monster)
    messages.success(request, f"{monster.name or monster.monster.name} ist {team.name} beigetreten")
    
    redirect_path = request.GET.get("redirect")
    return redirect(redirect_path if redirect_path and redirect_path.startswith("/dex/") else reverse("dex:monster_team_detail", args=[pk]))

@require_POST
@login_required
def delete_monster_from_team(request, pk):
    team = get_object_or_404(MonsterTeam, pk=pk, spieler__name=request.user.username)
    monster = get_object_or_404(SpielerMonster, pk=request.POST.get("monster_id"))
    team.monster.remove(monster)
    messages.success(request, f"{monster.name or monster.monster.name} ist aus {team.name} ausgetreten")

    redirect_path = request.GET.get("redirect")
    return redirect(redirect_path if redirect_path and redirect_path.startswith("/dex/") else reverse("dex:monster_team_detail", args=[pk]))

@require_POST
@login_required
def add_team_to_spielermonster(request, pk):
    sp_mo = get_object_or_404(SpielerMonster, pk=pk, spieler__name=request.user.username)
    team = get_object_or_404(MonsterTeam, pk=request.POST.get("team_id"))
    sp_mo.monsterteam_set.add(team)
    messages.success(request, f"{sp_mo.name or sp_mo.monster.name} ist {team.name} beigetreten")

    redirect_path = request.GET.get("redirect")
    return redirect(redirect_path if redirect_path and redirect_path.startswith("/dex/") else reverse("dex:monster_detail_farm", args=[pk]))

@require_POST
@login_required
def set_training_of_spielermonster(request, pk):
    sp_mo = get_object_or_404(SpielerMonster, pk=pk, spieler__name=request.user.username)
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

        lables = [label for stat, label in RangStat.StatType if stat in stats]
        messages.success(request, format_html(f"{sp_mo.name or sp_mo.monster.name} trainiert nun <b>{lables[0]}</b> und <b>{lables[1]}</b>!"))

    redirect_path = request.GET.get("redirect")
    return redirect(redirect_path if redirect_path and redirect_path.startswith("/dex/") else reverse("dex:monster_detail_farm", args=[pk]))

@require_POST
@login_required
def add_attack_to_spielermonster(request, pk):
    sp_mo = get_object_or_404(SpielerMonster, pk=pk, spieler__name=request.user.username)
    attack = get_object_or_404(Attacke, pk=request.POST.get("attack_id"))
    sp_mo.attacken.add(attack)
    messages.success(request, f"{sp_mo.name or sp_mo.monster.name} hat {attack.name} gelernt")

    redirect_path = request.GET.get("redirect")
    return redirect(redirect_path if redirect_path and redirect_path.startswith("/dex/") else reverse("dex:monster_detail_farm", args=[pk]))

@require_POST
@login_required
def delete_attack_from_spielermonster(request, pk):
    sp_mo = get_object_or_404(SpielerMonster, pk=pk, spieler__name=request.user.username)
    attack = get_object_or_404(Attacke, pk=request.POST.get("attack_id"))
    sp_mo.attacken.remove(attack)
    messages.success(request, f"{sp_mo.name or sp_mo.monster.name} hat {attack.name} verlernt")

    redirect_path = request.GET.get("redirect")
    return redirect(redirect_path if redirect_path and redirect_path.startswith("/dex/") else reverse("dex:monster_detail_farm", args=[pk]))

from math import floor
from random import choice
from typing import Iterable

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import Subquery, OuterRef, CharField, F, Value, Q, Count, Case, When
from django.db.models.functions import Coalesce, Concat, Cast
from django.db.models.query import QuerySet
from django.utils.html import format_html

from django_resized import ResizedImageField
from colorfield.fields import ColorField

from character.models import Spieler
from ppServer.utils import ConcatSubquery
from ..models import Dice, upload_and_rename_to_id



###### sub-models #########

class MonsterFähigkeit(models.Model):
    class Meta:
        ordering = ["name"]
        verbose_name = "Fähigkeit"
        verbose_name_plural = "Fähigkeiten"

    name = models.CharField(max_length=256, unique=True)
    description = models.TextField(verbose_name="Beschreibung")

    def __str__(self):
        return self.name


class Typ(models.Model):
    class Meta:
        ordering = ["name"]
        verbose_name = "Typ"
        verbose_name_plural = "Typen"

    color = ColorField(default='#B19071')
    text_color = ColorField(default='#070707')
    icon = ResizedImageField(size=[256, 256], upload_to=upload_and_rename_to_id, blank=True)

    name = models.CharField(max_length=128)

    stark_gegen = models.ManyToManyField("Typ", related_name="stark", related_query_name="stark", blank=True)
    schwach_gegen = models.ManyToManyField("Typ", related_name="schwach", related_query_name="schwach", blank=True)
    trifft_nicht = models.ManyToManyField("Typ", related_name="miss", related_query_name="miss", blank=True)

    def __str__(self):
        return self.name
    
    def tag(self):
        styles = f"color: {self.text_color}; background: {self.color}; font-weight: 500 !important; padding: .3em .5em; display: flex; justify-content: center; align-items: center; gap: .3em; border-radius: 300px; overflow: hidden;"

        if self.icon:
            icon_styles = f"mask-image: url({self.icon.url}); mask-position: center center; mask-repeat: no-repeat; mask-size: contain; -webkit-mask-image: url({self.icon.url}); -webkit-mask-position: center center; -webkit-mask-repeat: no-repeat; -webkit-mask-size: contain; background-color: {self.text_color}; height: 1.2em; aspect-ratio: 1"
            return format_html(f"<div style='{styles}'><span style='{icon_styles}' aria-hidden='true'></span>{self.name}</div>")

        else:
            return format_html(f"<div style='{styles}'>{self.name}</div>")
        
    @classmethod
    def get_type_efficiencies(cls, own_types: Iterable["Typ"]) -> {"is_miss": QuerySet["Typ"], "is_strong": QuerySet["Typ"], "is_weak": QuerySet["Typ"]}:
        context = {}

        # own_types = self.types.all()
        context["is_miss"] = Typ.objects.prefetch_related("trifft_nicht").filter(trifft_nicht__in=own_types).distinct()

        # calc raw values
        context["is_strong"] = Typ.objects.prefetch_related("stark_gegen").exclude(id__in=context["is_miss"]).annotate(
            value = Count(F("stark_gegen"), filter=Q(stark_gegen__in=own_types), distinct=False),
        )
        context["is_weak"] = Typ.objects.prefetch_related("schwach_gegen").exclude(id__in=context["is_miss"]).annotate(
            value = Count(F("schwach_gegen"), filter=Q(schwach_gegen__in=own_types), distinct=False),
        )

        # calc damage factor
        context["is_weak"] = context["is_weak"].annotate(
            counter = Coalesce(Subquery(context["is_strong"].filter(id=OuterRef("id")).values("value")[:1]), 0),
            damage_factor = 1.0 / 2**(F("value") - F("counter"))
        )
        context["is_strong"] = context["is_strong"].annotate(
            counter = Coalesce(Subquery(context["is_weak"].filter(id=OuterRef("id")).values("value")[:1]), 0),
            damage_factor = 1 + (F("value") - F("counter")) * 0.5
        )

        # filter based on opposing efficiency (-> see "keep")
        context["is_strong"] = context["is_strong"].filter(damage_factor__gt=1).order_by("name")
        context["is_weak"] = context["is_weak"].filter(damage_factor__lt=1).order_by("name")

        return context

    @classmethod
    def get_type_efficiencies_reverse(cls, own_types: Iterable["Typ"]) -> {"is_miss": QuerySet["Typ"], "is_strong": QuerySet["Typ"], "is_weak": QuerySet["Typ"]}:
        context = {}

        # own_types = self.types.all()
        context["is_miss"] = Typ.objects.prefetch_related("miss").filter(miss__in=own_types).distinct()

        # calc raw values
        context["is_strong"] = Typ.objects.prefetch_related("stark").exclude(id__in=context["is_miss"]).annotate(
            value = Count(F("stark"), filter=Q(stark__in=own_types), distinct=False),
        )
        context["is_weak"] = Typ.objects.prefetch_related("schwach").exclude(id__in=context["is_miss"]).annotate(
            value = Count(F("schwach"), filter=Q(schwach__in=own_types), distinct=False),
        )

        # calc damage factor
        context["is_weak"] = context["is_weak"].annotate(
            counter = Coalesce(Subquery(context["is_strong"].filter(id=OuterRef("id")).values("value")[:1]), 0),
            damage_factor = 1.0 / 2**(F("value") - F("counter"))
        )
        context["is_strong"] = context["is_strong"].annotate(
            counter = Coalesce(Subquery(context["is_weak"].filter(id=OuterRef("id")).values("value")[:1]), 0),
            damage_factor = 1 + (F("value") - F("counter")) * 0.5
        )

        # filter based on opposing efficiency (-> see "keep")
        context["is_strong"] = context["is_strong"].filter(damage_factor__gt=1).order_by("name")
        context["is_weak"] = context["is_weak"].filter(damage_factor__lt=1).order_by("name")

        return context


class Attacke(models.Model):
    class Meta:
        ordering = ["name"]
        verbose_name = "Attacke"
        verbose_name_plural = "Attacken"

    name = models.CharField(max_length=128, unique=True)
    damage = models.ManyToManyField(Dice, blank=True)
    description = models.TextField(verbose_name="Beschreibung")
    types = models.ManyToManyField(Typ, verbose_name="Typen")

    macht_schaden = models.BooleanField(default=False)
    macht_effekt = models.BooleanField(default=False)

    angriff_nahkampf = models.BooleanField(default=False)
    angriff_fernkampf = models.BooleanField(default=False)
    angriff_magie = models.BooleanField(default=False)
    verteidigung_geistig = models.BooleanField(default=False)
    verteidigung_körperlich = models.BooleanField(default=False)

    cost = models.PositiveSmallIntegerField(default=0, validators=[MaxValueValidator(7)], verbose_name="Kosten")

    draft = models.BooleanField(default=False)
    author = models.ForeignKey(Spieler, on_delete=models.SET_NULL, null=True, blank=True)
    monster_feddich = models.BooleanField(default=False)

    def __str__(self):
        return self.name
    
    class CardManager(models.Manager):

        def load_card(self):
            """ preloads all fields needed for display of monster-listentry """
            return self.prefetch_related("types", "damage")
    objects = CardManager()


class MonsterRang(models.Model):
    class Meta:
        ordering = ["rang"]
        verbose_name = "Monster-Rang"
        verbose_name_plural = "Monster-Ränge"

    rang = models.PositiveSmallIntegerField(unique=True)
    schadensWI = models.ManyToManyField(Dice, blank=True)
    reaktionsbonus = models.PositiveSmallIntegerField(default=0)
    angriffsbonus = models.PositiveSmallIntegerField(default=0)
    attackenpunkte = models.PositiveSmallIntegerField(default=0)

    def __str__(self):
        return f"Rang {self.rang}"


######## living things ########

class Monster(models.Model):
    class Meta:
        ordering = ["number"]
        verbose_name = "Monster"
        verbose_name_plural = "Monster"

    image = ResizedImageField(size=[1024, 1024], upload_to=upload_and_rename_to_id, blank=True)
    number = models.PositiveSmallIntegerField(unique=True)
    name = models.CharField(max_length=128)
    description = models.TextField(verbose_name="Beschreibung")
    habitat = models.TextField()
    fähigkeiten = models.ManyToManyField(MonsterFähigkeit, blank=True)
    
    wildrang = models.PositiveIntegerField(validators=[MinValueValidator(1)], default=1)
    weight = models.FloatField(validators=[MinValueValidator(0.001)], help_text="in kg", default=1)
    height = models.FloatField(validators=[MinValueValidator(0.001)], help_text="in Metern", default=1)

    base_initiative = models.SmallIntegerField(default=0)
    base_hp = models.SmallIntegerField(default=0)
    base_nahkampf = models.SmallIntegerField(default=0)
    base_fernkampf = models.SmallIntegerField(default=0)
    base_magie = models.SmallIntegerField(default=0)
    base_verteidigung_geistig = models.SmallIntegerField(default=0)
    base_verteidigung_körperlich = models.SmallIntegerField(default=0)

    base_schadensWI = models.ManyToManyField(Dice, blank=True)
    base_attackbonus = models.SmallIntegerField(default=0)
    base_reaktionsbonus = models.SmallIntegerField(default=0)


    alternativeForms = models.ManyToManyField("Monster", related_name="forms", related_query_name="forms", blank=True)
    opposites = models.ManyToManyField("Monster", related_name="opposite", related_query_name="opposite", blank=True)
    evolutionPre = models.ManyToManyField("Monster", related_name="evolution_pre", related_query_name="evolution_pre", blank=True)
    evolutionPost = models.ManyToManyField("Monster", related_name="evolution_post", related_query_name="evolution_post", blank=True)

    types = models.ManyToManyField(Typ, blank=True)
    attacken = models.ManyToManyField(Attacke, blank=True)
    visible = models.ManyToManyField(Spieler, blank=True)

    def __str__(self):
        return f"#{self.number} {self.name}"
    
    def basiswertsumme(self):
        return self.base_initiative + self.base_hp + self.base_nahkampf + self.base_fernkampf + self.base_magie + self.base_verteidigung_geistig + self.base_verteidigung_körperlich
    
    def get_type_efficiencies(self) -> {"is_miss": QuerySet[Typ], "is_strong": QuerySet[Typ], "is_weak": QuerySet[Typ]}:
        """ please prefetch monster.types """
        return Typ.get_type_efficiencies(self.types.all())

    class RangManager(models.Manager):

        def get_queryset(self) -> QuerySet:
            """ adds 'base_schadensWI_str' field """
            schadensWI_qs = Dice.objects.filter(monster__id= OuterRef("id")).annotate(
                str=Concat(Cast("amount", output_field=CharField()), F("type"), output_field=CharField())
            ).values("str")

            return super().get_queryset().annotate(
                base_schadensWI_str = ConcatSubquery(schadensWI_qs, separator=" + "),
            )

        def with_rang(self):
            """ adds 'rang_reaktionsbonus', 'rang_angriffsbonus' and 'rang_schadensWI_str' fields. """

            rang_qs = MonsterRang.objects.filter(rang__lte=OuterRef("wildrang")).order_by("-rang")[:1]
            
            schadensWI_qs = Dice.objects.filter(monsterrang__rang= OuterRef("rang_rang")).annotate(
                str=Concat(Cast("amount", output_field=CharField()), F("type"), output_field=CharField())
            ).values("str")

            return self.prefetch_related("base_schadensWI", "types").annotate(
                rang_rang = Subquery(rang_qs.values("rang")),
                rang_reaktionsbonus = Subquery(rang_qs.values("reaktionsbonus")),
                rang_angriffsbonus = Subquery(rang_qs.values("angriffsbonus")),
                rang_schadensWI_str = ConcatSubquery(schadensWI_qs, separator=" + "),
            )
        def load_card(self):
            """ preloads all fields needed for display of monster-listentry. 'spieler' needs to be a variable to the template, too!"""
            return self.prefetch_related("types", "visible")
    objects = RangManager()


class RangStat(models.Model):
    class Meta:
        ordering = ["spielermonster", "stat"]
        verbose_name = "Rang Stat"
        verbose_name_plural = "Rang Stats"

    StatType = [
        ("INI", "Initiative"),
        ("HP", "HP"),
        ("N", "Nahkampf"),
        ("F", "Fernkampf"),
        ("MA", "Magie"),
        ("VER_G", "Verteidigung geistig"),
        ("VER_K", "Verteidigung körperlich"),
    ]
    POLLS_PER_RANG = 2
    STAT_RANG0_MAX_WERT = 10    # for display as chart only
    WEIGHT_BASE = 1
    WEIGHT_SKILLED = 2
    WEIGHT_TRAINED = 3
    AMOUNT_SKILLED = 2
    AMOUNT_TRAINED = 3
    
    spielermonster = models.ForeignKey("SpielerMonster", on_delete=models.CASCADE)
    stat = models.CharField(max_length=5, choices=StatType)
    
    wert = models.PositiveSmallIntegerField(default=0)
    skilled = models.BooleanField(default=False)
    trained = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.stat}: {self.wert}"

class SpielerMonsterAttack(models.Model):

    class Meta:
        verbose_name = "Attacke"
        verbose_name_plural = "Attacken"
        unique_together = [("attacke", "spieler_monster")]

    attacke = models.ForeignKey(Attacke, on_delete=models.CASCADE)
    spieler_monster = models.ForeignKey("SpielerMonster", on_delete=models.CASCADE)

    cost = models.PositiveSmallIntegerField()


class SpielerMonster(models.Model):

    class Meta:
        ordering = ["spieler", "monster", "name"]
        verbose_name = "Spieler-Monster"
        verbose_name_plural = "Spieler-Monster"
    
    ARTSPEZIFISCHER_RANGFAKTOR = 20
    MAX_AMOUNT_ATTACKEN = 5


    spieler = models.ForeignKey(Spieler, on_delete=models.CASCADE)
    monster = models.ForeignKey(Monster, on_delete=models.CASCADE)
    gefangen_am = models.DateField(auto_now_add=True)

    name = models.CharField(max_length=256, null=True, blank=True)
    rang = models.SmallIntegerField()
    attacken = models.ManyToManyField(Attacke, through=SpielerMonsterAttack)

    attackenpunkte = models.SmallIntegerField(default=0)

    def __str__(self):
        return f"{self.name or self.monster} von {self.spieler}"
    
    def max_cost_attack(self):
        return floor(self.rang / 10)+1
    
    def get_buyable_attacks(self) -> QuerySet[Attacke]:
        max_cost = min(self.attackenpunkte, self.max_cost_attack())

        return self.monster.attacken.all()\
            .prefetch_related("types")\
            .annotate(
                types_count = Count("types__pk", distinct=True),
                stab_count = Count("types__pk", filter=Q(types__monster=self.monster), distinct=True),
                discount = Case(When(cost=0, then=0), default=F("cost")-1, output_field=models.PositiveSmallIntegerField()),
                modified_cost = Case(When(types_count=F("stab_count"), then=F("discount")), default=F("cost"), output_field=models.PositiveSmallIntegerField()),
            )\
            .filter(Q(modified_cost__lte=max_cost))\
            .exclude(id__in=self.attacken.values_list("spielermonsterattack__attacke", flat=True))\
            .exclude(draft=True)\
            .order_by("name")


    def level_up(self):

        # collect stat pool
        pool = []
        for stat in self.rangstat_set.all():
            amount = RangStat.WEIGHT_BASE
            if stat.skilled: amount += RangStat.WEIGHT_SKILLED
            if stat.trained: amount += RangStat.WEIGHT_TRAINED
            for _ in range(amount): pool.append(stat.stat)

        # poll from stats
        polls = []
        for _ in range(RangStat.POLLS_PER_RANG):
            polls.append(choice(pool))
            pool = [p for p in pool if p not in polls]

        # increase polled stats
        stats = []
        for stat in self.rangstat_set.filter(stat__in=polls):
            stat.wert += 1
            stats.append(stat)

        RangStat.objects.bulk_update(stats, fields=["wert"])


    class RangManager(models.Manager):

        def get_queryset(self) -> QuerySet:
            """ adds 'base_schadensWI_str' field """
            schadensWI_qs = Dice.objects.filter(monster= OuterRef("monster")).annotate(
                str=Concat(Cast("amount", output_field=CharField()), F("type"), output_field=CharField())
            ).values("str")

            return super().get_queryset().annotate(
                base_schadensWI_str = ConcatSubquery(schadensWI_qs, separator=" + "),
            )

        def with_rang_and_stats(self):
            """ adds 'rang_reaktionsbonus', 'rang_angriffsbonus' and 'rang_schadensWI_str' fields. """

            stat_qs = RangStat.objects.filter(spielermonster__id=OuterRef("id"))
            rang_qs = MonsterRang.objects.filter(rang__lte=OuterRef("rang")).order_by("-rang")[:1]
            
            schadensWI_qs = Dice.objects.filter(monsterrang__rang= OuterRef("rang_rang")).annotate(
                str=Concat(Cast("amount", output_field=CharField()), F("type"), output_field=CharField())
            ).values("str")

            return self.prefetch_related("monster").annotate(
                rang_rang = Subquery(rang_qs.values("rang")),
                rang_faktor = 1.0 * (F("rang") + SpielerMonster.ARTSPEZIFISCHER_RANGFAKTOR) / SpielerMonster.ARTSPEZIFISCHER_RANGFAKTOR,
                rang_reaktionsbonus = Subquery(rang_qs.values("reaktionsbonus")),
                rang_angriffsbonus = Subquery(rang_qs.values("angriffsbonus")),
                rang_schadensWI_str = ConcatSubquery(schadensWI_qs, separator=" + "),

                initiative = Cast(F("monster__base_initiative") * F("rang_faktor") + Subquery(stat_qs.filter(stat="INI").values("wert")[:1]), output_field=models.IntegerField()),
                hp = Cast(F("monster__base_hp") * F("rang_faktor") + Subquery(stat_qs.filter(stat="HP").values("wert")[:1]), output_field=models.IntegerField()),
                nahkampf = Cast(F("monster__base_nahkampf") * F("rang_faktor") + Subquery(stat_qs.filter(stat="N").values("wert")[:1]), output_field=models.IntegerField()),
                fernkampf = Cast(F("monster__base_fernkampf") * F("rang_faktor") + Subquery(stat_qs.filter(stat="F").values("wert")[:1]), output_field=models.IntegerField()),
                magie = Cast(F("monster__base_magie") * F("rang_faktor") + Subquery(stat_qs.filter(stat="MA").values("wert")[:1]), output_field=models.IntegerField()),
                verteidigung_geistig = Cast(F("monster__base_verteidigung_geistig") * F("rang_faktor") + Subquery(stat_qs.filter(stat="VER_G").values("wert")[:1]), output_field=models.IntegerField()),
                verteidigung_körperlich = Cast(F("monster__base_verteidigung_körperlich") * F("rang_faktor") + Subquery(stat_qs.filter(stat="VER_K").values("wert")[:1]), output_field=models.IntegerField()),

                skilled_stats = Concat(Value(" "), ConcatSubquery(stat_qs.filter(skilled=True).values("stat"), separator=" "), Value(" ")),
                trained_stats = Concat(Value(" "), ConcatSubquery(stat_qs.filter(trained=True).values("stat"), separator=" "), Value(" ")),
            )
    objects = RangManager()


class MonsterTeam(models.Model):

    class Meta:
        ordering = ["spieler", "name"]
        verbose_name = "Monster-Team"
        verbose_name_plural = "Monster-Teams"

    farbe = ColorField(default='#0000FF', blank=True)
    textfarbe = ColorField(default='#FFFFFF', blank=True)
    name = models.CharField(max_length=256, unique=True)
    spieler = models.ForeignKey(Spieler, on_delete=models.CASCADE)
    monster = models.ManyToManyField(SpielerMonster)

    def __str__(self):
        return f"Team {self.name} von {self.spieler}"

    def get_type_efficiencies(self) -> {"is_strong": list[dict["type": Typ, "count": int]], "is_weak_or_miss": list[dict["type": Typ, "count": int]]}:
        """ please prefetch self.monster.monster.types """

        is_strong = []
        is_weak_or_miss = []

        for sp_mo in self.monster.all():
            eff = Typ.get_type_efficiencies(sp_mo.monster.types.all())

            is_strong.extend(list(eff["is_strong"]))
            is_weak_or_miss.extend(list(eff["is_weak"]))
            is_weak_or_miss.extend(list(eff["is_miss"]))

        return {
            "is_strong": [{"type": type, "count": is_strong.count(type)} for type in sorted(set(is_strong), key=lambda o: o.name)],
            "is_weak_or_miss": [{"type": type, "count": is_weak_or_miss.count(type)} for type in sorted(set(is_weak_or_miss), key=lambda o: o.name)],
        }
    
    def get_attack_coverage(self):
        """ please prefetch self.monster.monster.attacken.types """

        hit_types = []
        for monster in self.monster.all():
            for attack in monster.attacken.all():
                hit_types.extend(Typ.get_type_efficiencies_reverse(attack.types.all())["is_strong"])

        coverage = [{"type": t, "count": hit_types.count(t)} for t in sorted(set(hit_types), key=lambda o: o.name)]

        return {
            "attack_coverage": coverage,
            "no_attack_coverage": Typ.objects.exclude(id__in=[t["type"].id for t in coverage])
        }
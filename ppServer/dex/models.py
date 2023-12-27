import re
from math import floor
from random import choice

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import Subquery, OuterRef, CharField, F, Value
from django.db.models.functions import Concat, Cast
from django.db.models.query import QuerySet
from django.utils.html import format_html

from django_resized import ResizedImageField
from colorfield.fields import ColorField

from character.models import Spieler

from .utils import ConcatSubquery


###### utils ########

def upload_and_rename_to_id(instance, filename):
    file_extension = filename.split('.')[::-1][0]
    if hasattr(instance, "number"):
        filename_name = instance.number
    elif hasattr(instance, "name"):
        filename_name =instance.name
    else:
        filename_name = f"{instance.plant}-{instance.phase}"


    return f"dex/{instance._meta.verbose_name}/{filename_name}.{file_extension}"


class Dice(models.Model):
    class Meta:
        ordering = ["type", "amount"]
        verbose_name = "Dice"
        verbose_name_plural = "Dice"
        unique_together = ("amount", "type")

    DiceType = models.TextChoices("DiceType", "W2 W3 W4 W6 W8 W10 W12 W20 W100")

    amount = models.SmallIntegerField(default=1)
    type = models.CharField(max_length=4, choices=DiceType.choices)

    def __str__(self):
        return f"{self.amount}{self.type}"

    @classmethod
    def toString(cls, *dices: list[str], separator=" + ") -> str:
        """
            collects same dice types together.
            concats different types with the provided separator.
            returns resulting string.
        """
        pool = {}
        for dice in [d for d in dices if re.match("^\d+W\d+$", d)]:
            [amount, type] = dice.split("W")
            pool[type] = int(amount) if type not in pool else pool[type] + int(amount)
        return separator.join([f"{pool[type]}W{type}" for type in sorted(pool.keys(), key=lambda x: int(x), reverse=True)])


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
    attacken = models.ManyToManyField(Attacke)

    attackenpunkte = models.SmallIntegerField(default=0)

    def __str__(self):
        return f"{self.name or self.monster} von {self.spieler}"
    
    def max_cost_attack(self):
        return floor(self.rang / 10)+1


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
        for stat in self.rangstat_set.filter(stat__in=polls):
            stat.wert += 1
            stat.save(update_fields=["wert"])


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


class ParaPflanzenImage(models.Model):
    class Meta:
        ordering = ["plant", "phase"]
        verbose_name = "Para-Pflanzenbild"
        verbose_name_plural = "Para-Pflanzenbilder"
        unique_together = ("plant", "phase")

    plant = models.ForeignKey("ParaPflanze", on_delete=models.CASCADE)
    image = ResizedImageField(size=[1024, 1024], upload_to=upload_and_rename_to_id)
    phase = models.PositiveSmallIntegerField(default=1)
    aussehen = models.TextField()

    is_vorschau = models.BooleanField(default=False)

class ParaPflanze(models.Model):
    class Meta:
        ordering = ["id"]
        verbose_name = "Para-Pflanze"
        verbose_name_plural = "Para-Pflanzen"
        unique_together = ("generation", "number")

    Licht = models.IntegerChoices("Licht", "0/4 1/4 2/4 3/4 4/4")
    Boden = models.IntegerChoices("Boden", "weich mittel hart")
    Wasser = models.IntegerChoices("Wasser", "wenig mittel viel")
    Krankheit = models.IntegerChoices("Krankheit", "sehr_gering gering mäßig hoch sehr_hoch extrem_hoch")
    
    name = models.CharField(max_length=128)
    generation = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(4)], default=1)
    number = models.PositiveSmallIntegerField(validators=[MinValueValidator(1)], default=1)
    phasen = models.PositiveSmallIntegerField(validators=[MinValueValidator(1)], default=5)

    erholungsphase = models.TextField()
    vermehrung = models.TextField()
    nahrung = models.TextField()
    standort = models.TextField()
    besonderheiten = models.TextField()
    pH = models.FloatField(validators=[MinValueValidator(-4), MaxValueValidator(20)], default=7)
    temperature = models.FloatField(validators=[MinValueValidator(-30), MaxValueValidator(50)], default=10, help_text="in °C")
    licht = models.PositiveSmallIntegerField(choices=Licht.choices, default=3)
    boden = models.PositiveSmallIntegerField(choices=Boden.choices, default=2)
    wasser = models.PositiveSmallIntegerField(choices=Wasser.choices, default=2)
    soziale_bedürfnisse = models.SmallIntegerField(validators=[MinValueValidator(-3), MaxValueValidator(3)], default=0, help_text="von -3 bis 3")
    krankheitsanfälligkeit = models.SmallIntegerField(choices=Krankheit.choices, default=3)
    größe = models.FloatField(validators=[MinValueValidator(0.001)], default=1, help_text="in Metern")

    def __str__(self):
        return self.name


class Fertigkeit(models.Model):
    class Meta:
        ordering = ["name"]
        verbose_name = "Fertigkeit"
        verbose_name_plural = "Fertigkeiten"

    name = models.CharField(max_length=64, unique=True)


class ParaTierFertigkeit(models.Model):
    class Meta:
        ordering = ["tier", "fertigkeit"]
        verbose_name = "Fertigkeit (Para-Tier)"
        verbose_name_plural = "Fertigkeiten (Para-Tier)"

    tier = models.ForeignKey("ParaTier", on_delete=models.CASCADE)
    fertigkeit = models.ForeignKey(Fertigkeit, on_delete=models.CASCADE)

    pool = models.PositiveSmallIntegerField(default=5, help_text="W6")

class ParaTier(models.Model):
    class Meta:
        ordering = ["name"]
        verbose_name = "Para-Tier"
        verbose_name_plural = "Para-Tiere"

    name = models.CharField(max_length=128)
    image = ResizedImageField(size=[1024, 1024], upload_to=upload_and_rename_to_id, blank=True)
    description = models.TextField(verbose_name="Beschreibung")
    habitat = models.TextField()

    fertigkeiten = models.ManyToManyField(Fertigkeit, through=ParaTierFertigkeit)


class GeschöpfFertigkeit(models.Model):
    class Meta:
        ordering = ["geschöpf", "fertigkeit"]
        verbose_name = "Fertigkeit (Geschöpf)"
        verbose_name_plural = "Fertigkeiten (Geschöpf)"

    geschöpf = models.ForeignKey("Geschöpf", on_delete=models.CASCADE)
    fertigkeit = models.ForeignKey(Fertigkeit, on_delete=models.CASCADE)

    pool = models.PositiveSmallIntegerField(default=5, help_text="W6")

class Geschöpf(models.Model):
    class Meta:
        ordering = ["name"]
        verbose_name = "Geschöpf"
        verbose_name_plural = "Geschöpfe"

    Gefahr = [
        ("S", "sicher"),
        ("B", "bedenklich"),
        ("L", "lethal"),
        ("H", "hortend"),
    ]
    Status = models.IntegerChoices("Status", "gefangen ausgebrochen noch_frei tot Existenz_noch_unsicher")

    image = ResizedImageField(size=[1024, 1024], upload_to=upload_and_rename_to_id, blank=True)
    name = models.CharField(max_length=128)
    number = models.PositiveSmallIntegerField(unique=True)
    gefahrenklasse = models.CharField(choices=Gefahr, default="B")
    verwahrungsklasse = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)], default=3)
    status = models.PositiveSmallIntegerField(choices=Status.choices, default=5)

    verhalten = models.TextField()
    gefahren_fähigkeiten = models.TextField()
    gefahrenprävention = models.TextField()
    aufenthaltsort = models.TextField()
    forschungsstand = models.TextField()
    initiative = models.ForeignKey(Dice, on_delete=models.SET_NULL, null=True, blank=True, related_name="initiative")
    hp = models.PositiveSmallIntegerField()
    schaWI = models.ManyToManyField(Dice, related_name="schadensWI")
    reaktion = models.PositiveSmallIntegerField(default=0)


    fertigkeiten = models.ManyToManyField(Fertigkeit, through=GeschöpfFertigkeit)

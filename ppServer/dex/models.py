import re

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from django_resized import ResizedImageField

from character.models import Spieler


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

class ParaPflanzeÖkologie(models.Model):
    class Meta:
        ordering = ["plant", "factor"]
        verbose_name = "Para-Pflanzenbild"
        verbose_name_plural = "Para-Pflanzenbilder"
        unique_together = ("plant", "factor", "x")

    factor_enum = [
        ("p", "pH"),
        ("t", "Temperatur"),
        ("l", "Licht"),
        ("w", "Wasser"),
    ]

    plant = models.ForeignKey("ParaPflanze", on_delete=models.CASCADE)
    factor = models.CharField(max_length=1, choices=factor_enum)

    x = models.FloatField(null=False, blank=False)
    y = models.FloatField(null=False, blank=False)

class ParaPflanze(models.Model):
    class Meta:
        ordering = ["id"]
        verbose_name = "Para-Pflanze"
        verbose_name_plural = "Para-Pflanzen"
        unique_together = ("generation", "number")

    Boden = models.IntegerChoices("Boden", "weich mittel hart")
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
    boden = models.PositiveSmallIntegerField(choices=Boden.choices, default=2)
    soziale_bedürfnisse = models.SmallIntegerField(validators=[MinValueValidator(-3), MaxValueValidator(3)], default=0, help_text="von -3 bis 3")
    krankheitsanfälligkeit = models.SmallIntegerField(choices=Krankheit.choices, default=3)
    größe = models.FloatField(validators=[MinValueValidator(0.001)], default=1, help_text="in Metern")

    visible = models.ManyToManyField(Spieler, blank=True)

    def __str__(self):
        return self.name
    
    def ecology(self) -> dict[ParaPflanzeÖkologie.factor_enum, list[ParaPflanzeÖkologie]]:
        qs = self.parapflanzeökologie_set
        return {label: list(qs.filter(factor=char).values("x", "y")) for char, label in ParaPflanzeÖkologie.factor_enum }


class Fertigkeit(models.Model):
    class Meta:
        ordering = ["name"]
        verbose_name = "Fertigkeit"
        verbose_name_plural = "Fertigkeiten"

    name = models.CharField(max_length=64, unique=True)

    def __str__(self):
        return self.name


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
        ordering = ["number"]
        verbose_name = "Geschöpf"
        verbose_name_plural = "Geschöpfe"

    Gefahr = [
        ("S", "sicher"),
        ("B", "bedenklich"),
        ("L", "letal"),
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
    schadensWI = models.ManyToManyField(Dice, related_name="schadensWI")
    reaktion = models.PositiveSmallIntegerField(default=0)


    fertigkeiten = models.ManyToManyField(Fertigkeit, through=GeschöpfFertigkeit)
    visible = models.ManyToManyField(Spieler, blank=True)

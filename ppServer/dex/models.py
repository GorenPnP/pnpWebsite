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

    DiceType = models.TextChoices("DiceType", "W2 W4 W6 W8 W10 W12 W20 W100")

    amount = models.SmallIntegerField(default=1)
    type = models.CharField(max_length=4, choices=DiceType.choices)

    def __str__(self):
        return f"{self.amount}{self.type}"


###### sub-models #########

# class Fertigkeit(models.Model):
#     class Meta:
#         ordering = ["id"]
#         verbose_name = ""
#         verbose_name_plural = ""

class Typ(models.Model):
    class Meta:
        ordering = ["name"]
        verbose_name = "Typ"
        verbose_name_plural = "Typen"

    icon = ResizedImageField(size=[256, 256], upload_to=upload_and_rename_to_id)
    name = models.CharField(max_length=128)
    stark_gegen = models.ManyToManyField("Typ", related_name="stark", related_query_name="stark", blank=True)
    schwach_gegen = models.ManyToManyField("Typ", related_name="schwach", related_query_name="schwach", blank=True)
    trifft_nicht = models.ManyToManyField("Typ", related_name="miss", related_query_name="miss", blank=True)

    def __str__(self):
        return self.name

class Attacke(models.Model):
    class Meta:
        ordering = ["name"]
        verbose_name = "Attacke"
        verbose_name_plural = "Attacken"

    name = models.CharField(max_length=128, unique=True)
    damage = models.ManyToManyField(Dice, blank=True)
    description = models.TextField()
    types = models.ManyToManyField(Typ)

    macht_schaden = models.BooleanField(default=False)
    macht_effekt = models.BooleanField(default=False)

    def __str__(self):
        return self.name


######## living things ########

class Monster(models.Model):
    class Meta:
        ordering = ["number"]
        verbose_name = "Monster"
        verbose_name_plural = "Monster"

    image = ResizedImageField(size=[1024, 1024], upload_to=upload_and_rename_to_id)
    number = models.PositiveSmallIntegerField(unique=True)
    name = models.CharField(max_length=128)
    description = models.TextField()
    habitat = models.TextField()
    
    wildrang = models.PositiveIntegerField(validators=[MinValueValidator(1)], default=1)
    weight = models.FloatField(validators=[MinValueValidator(0.001)], help_text="in kg", default=1)
    height = models.FloatField(validators=[MinValueValidator(0.001)], help_text="in Metern", default=1)
    
    base_hp = models.PositiveIntegerField(default=1)
    base_schadensWI = models.ManyToManyField(Dice)

    alternativeForms = models.ManyToManyField("Monster", related_name="forms", related_query_name="forms", blank=True)
    opposites = models.ManyToManyField("Monster", related_name="opposite", related_query_name="opposite", blank=True)
    evolutionPre = models.ManyToManyField("Monster", related_name="evolution_pre", related_query_name="evolution_pre", blank=True)
    evolutionPost = models.ManyToManyField("Monster", related_name="evolution_post", related_query_name="evolution_post", blank=True)

    types = models.ManyToManyField(Typ, blank=True)
    attacken = models.ManyToManyField(Attacke, blank=True)
    visible = models.ManyToManyField(Spieler, blank=True)

    def __str__(self):
        return f"#{self.number} {self.name}"


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

# class ParaTier(models.Model):
#     class Meta:
#         ordering = ["id"]
#         verbose_name = ""
#         verbose_name_plural = ""

# class Geschöpf(models.Model):
#     class Meta:
#         ordering = ["id"]
#         verbose_name = ""
#         verbose_name_plural = ""

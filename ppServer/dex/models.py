from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.html import format_html

from django_resized import ResizedImageField
from colorfield.fields import ColorField

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

class MonsterFähigkeit(models.Model):
    class Meta:
        ordering = ["name"]
        verbose_name = "Fähigkeit"
        verbose_name_plural = "Fähigkeiten"

    name = models.CharField(max_length=256, unique=True)
    description = models.TextField(verbose_name="Beschreibung")

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
        styles = f"max-width: 80px; color: {self.text_color}; background: {self.color}; font-weight: 500 !important; padding: .3em .5em; display: flex; justify-content: center; align-items: center; gap: .3em; border-radius: 300px; overflow: hidden;"

        if self.icon:
            return format_html(f"<div style='{styles}'><img src='{self.icon.url}' style='height: 1.2em; aspect-ratio: 1'>{self.name}</div>")

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

    image = ResizedImageField(size=[1024, 1024], upload_to=upload_and_rename_to_id, blank=True)
    number = models.PositiveSmallIntegerField(unique=True)
    name = models.CharField(max_length=128)
    description = models.TextField(verbose_name="Beschreibung")
    habitat = models.TextField()
    fähigkeiten = models.ManyToManyField(MonsterFähigkeit, blank=True)
    
    wildrang = models.PositiveIntegerField(validators=[MinValueValidator(1)], default=1)
    weight = models.FloatField(validators=[MinValueValidator(0.001)], help_text="in kg", default=1)
    height = models.FloatField(validators=[MinValueValidator(0.001)], help_text="in Metern", default=1)
    
    base_hp = models.PositiveIntegerField(default=1)
    base_schadensWI = models.ManyToManyField(Dice, blank=True)

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

    Gefahr = models.IntegerChoices("Gefahr", "sicher bedenklich lethal hortend")
    Status = models.IntegerChoices("Status", "gefangen ausgebrochen noch_frei tot Existenz_noch_unsicher")

    name = models.CharField(max_length=128)
    number = models.PositiveSmallIntegerField(unique=True)
    gefahrenklasse = models.PositiveSmallIntegerField(choices=Gefahr.choices, default=1)
    verwahrungsklasse = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)], default=3)
    status = models.PositiveSmallIntegerField(choices=Status.choices, default=5)
    verhalten = models.TextField()
    gefahren_fähigkeiten = models.TextField()
    gefahrenprävention = models.TextField()
    aufenthaltsort = models.TextField()
    forschungsstand = models.TextField()
    hp = models.PositiveSmallIntegerField()
    schaWI = models.ManyToManyField(Dice)
    reaktion = models.PositiveSmallIntegerField(default=0)


    image = ResizedImageField(size=[1024, 1024], upload_to=upload_and_rename_to_id, blank=True)
    fertigkeiten = models.ManyToManyField(Fertigkeit, through=GeschöpfFertigkeit)

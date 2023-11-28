from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from django_resized import ResizedImageField

from character.models import Spieler


###### utils ########

def upload_and_rename_to_id(instance, filename):
    file_extension = filename.split('.')[::-1][0]
    filename_name = instance.number if hasattr(instance, "number") else instance.name

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

# class ParaPflanze(models.Model):
#     class Meta:
#         ordering = ["id"]
#         verbose_name = ""
#         verbose_name_plural = ""

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

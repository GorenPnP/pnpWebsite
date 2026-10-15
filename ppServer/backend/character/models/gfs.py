from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from django_resized import ResizedImageField
from markdownfield.models import MarkdownField, RenderedMarkdownField
from markdownfield.validators import VALIDATOR_STANDARD

from shop.models import Engelsroboter

from .base import Wesenkraft


class Wesen(models.Model):

    class Meta:
        ordering = ['komplexität']
        verbose_name = "Wesen"
        verbose_name_plural = "Wesen"

    komplexität = models.PositiveIntegerField(default=0)

    icon = ResizedImageField(size=[64, 64], null=True, blank=True)
    titel = models.CharField(max_length=20, unique=True)
    beschreibung = MarkdownField(rendered_field='beschreibung_rendered', validator=VALIDATOR_STANDARD, blank=True)
    beschreibung_rendered = RenderedMarkdownField(null=True, blank=True)

    def __str__(self):
        return self.titel


class GfsEigenschaft(models.Model):

    class Meta:
        verbose_name = "Gfs-Eigenschaft"
        verbose_name_plural = "Gfs-Eigenschaften"

        ordering = ["name"]

    name = models.CharField(max_length=128, unique=True)
    beschreibung = models.TextField(blank=True, null=True)

    def __str__(self): return self.name


class GfsImage(models.Model):

    class Meta:
        verbose_name = "Bild"
        verbose_name_plural = "Bilder"

        ordering = ["gfs", "order"]

    gfs = models.ForeignKey("Gfs", on_delete=models.CASCADE)
    order = models.FloatField(default=1.0)

    img = ResizedImageField(size=[1024, 1024])
    text = models.TextField(blank=True, null=True)

    def __str__(self): return self.text if self.text else "-"


class Gfs(models.Model):

    class Meta:
        ordering = ['titel']
        verbose_name = "Gfs/Genere"
        verbose_name_plural = "Gfs/Genere"

    DIFFICULTY_ENUM = [
        ("e", "für Einsteiger"),
        ("f", "für Fortgeschrittene"),
        ("p", "für Profis"),
    ]

    icon = ResizedImageField(size=[64, 64], null=True, blank=True)

    titel = models.CharField(max_length=30, unique=True)
    wesen = models.ForeignKey(Wesen, on_delete=models.SET_NULL, blank=True, null=True)
    beschreibung = MarkdownField(rendered_field='beschreibung_rendered', validator=VALIDATOR_STANDARD)
    beschreibung_rendered = RenderedMarkdownField(null=True)
    eigenschaften = models.ManyToManyField(GfsEigenschaft, blank=True)

    ap = models.PositiveIntegerField(default=0, validators=[MaxValueValidator(100)], verbose_name="AP-Kosten")

    base_movement_speed = models.FloatField(default=3, null=False, blank=True, verbose_name="Grundbewegungsrate")
    wesenschaden_waff_kampf = models.IntegerField("BS", default=0)
    wesenschaden_andere_gestalt = models.IntegerField(
        "BS andere Gestalt", blank=True, null=True)

    startmanifest = models.DecimalField('Startmanifest', max_digits=4, decimal_places=2, default=10.0,
                                        validators=[MaxValueValidator(10), MinValueValidator(0)])

    attribute = models.ManyToManyField('Attribut', through='GfsAttribut')
    fertigkeiten = models.ManyToManyField("Fertigkeit", through="GfsFertigkeit")

    vorteile = models.ManyToManyField('Vorteil', through="GfsVorteil", blank=True)
    nachteile = models.ManyToManyField('Nachteil', through="GfsNachteil", blank=True)
    wesenkraft = models.ManyToManyField('Wesenkraft', through="GfsWesenkraft")

    difficulty = models.CharField(max_length=1, choices=DIFFICULTY_ENUM, default=DIFFICULTY_ENUM[0][0], verbose_name=".. leicht/mittel/schwer zu spielen sein?")

    def __str__(self):
        return self.titel

    def relAttributQueryset(self):
        return GfsAttribut.objects.filter(gfs=self)

    def relVorteilQueryset(self):
        return GfsVorteil.objects.filter(gfs=self)

    def relNachteilQueryset(self):
        return GfsNachteil.objects.filter(gfs=self)


class GfsAttribut(models.Model):
    class Meta:
        ordering = ['attribut']
        verbose_name = "Startattribut"
        verbose_name_plural = "Startattribute"
        unique_together = ["attribut", "gfs"]

    attribut = models.ForeignKey('Attribut', on_delete=models.CASCADE)
    gfs = models.ForeignKey(Gfs, on_delete=models.CASCADE)

    aktuellerWert = models.IntegerField(default=0)
    maxWert = models.IntegerField(default=0)


class GfsFertigkeit(models.Model):

    class Meta:
        ordering = ['gfs', 'fertigkeit']
        verbose_name = "Fertigkeit"
        verbose_name_plural = "Fertigkeiten"

        unique_together = (('gfs', 'fertigkeit'),)

    gfs = models.ForeignKey(Gfs, on_delete=models.CASCADE)
    fertigkeit = models.ForeignKey("Fertigkeit", on_delete=models.CASCADE)

    fp = models.IntegerField(default=0)

    def __str__(self):
        return "'{}' von '{}'".format(self.fertigkeit.__str__(), self.gfs.__str__())


class GfsWesenkraft(models.Model):

    class Meta:
        ordering = ['gfs', 'wesenkraft']
        verbose_name = "Start-Wesenkraft von Gfs"
        verbose_name_plural = "Start-Wesenkräfte von Gfs"

        unique_together = (('gfs', 'wesenkraft'),)

    gfs = models.ForeignKey(Gfs, on_delete=models.CASCADE)
    wesenkraft = models.ForeignKey(Wesenkraft, on_delete=models.CASCADE)

    def __str__(self):
        return "{} ({})".format(self.wesenkraft, self.gfs.__str__())


class GfsVorteil(models.Model):
    class Meta:
        ordering = ['teil']
        verbose_name = "Startvorteil"
        verbose_name_plural = "Startvorteile"
        unique_together = ["teil", "gfs", "notizen"]

    teil = models.ForeignKey('Vorteil', on_delete=models.CASCADE)
    gfs = models.ForeignKey(Gfs, on_delete=models.CASCADE)

    notizen = models.CharField(max_length=100, default='', blank=True)

    attribut = models.ForeignKey("Attribut", on_delete=models.SET_NULL, null=True, blank=True)
    fertigkeit = models.ForeignKey("Fertigkeit", on_delete=models.SET_NULL, null=True, blank=True)
    engelsroboter = models.ForeignKey(Engelsroboter, on_delete=models.SET_NULL, null=True, blank=True)
    ip = models.PositiveSmallIntegerField(null=True, blank=True)

    is_sellable = models.BooleanField(default=True, verbose_name="ist verkaufbar?")


class GfsNachteil(models.Model):
    class Meta:
        ordering = ['teil']
        verbose_name = "Startnachteil"
        verbose_name_plural = "Startnachteile"
        unique_together = ["teil", "gfs", "notizen"]

    teil = models.ForeignKey('Nachteil', on_delete=models.CASCADE)
    gfs = models.ForeignKey(Gfs, on_delete=models.CASCADE)

    notizen = models.CharField(max_length=100, default='', blank=True)

    attribut = models.ForeignKey("Attribut", on_delete=models.SET_NULL, null=True, blank=True)
    fertigkeit = models.ForeignKey("Fertigkeit", on_delete=models.SET_NULL, null=True, blank=True)
    engelsroboter = models.ForeignKey(Engelsroboter, on_delete=models.SET_NULL, null=True, blank=True)
    ip = models.PositiveSmallIntegerField(null=True, blank=True)

    is_sellable = models.BooleanField(default=True, verbose_name="ist verkaufbar?")


class GfsZauber(models.Model):
    class Meta:
        ordering = ['gfs', "item"]
        verbose_name = "Startzauber"
        verbose_name_plural = "Startzauber"
        unique_together = ["item", "gfs"]

    item = models.ForeignKey('shop.Zauber', on_delete=models.CASCADE)
    gfs = models.ForeignKey(Gfs, on_delete=models.CASCADE)

    tier = models.PositiveSmallIntegerField(default=0, validators=[MaxValueValidator(7)])


class GfsStufenplanBase(models.Model):
    class Meta:
        ordering = ["stufe"]
        verbose_name = "Gfs Basis-Stufenplan"
        verbose_name_plural = "Gfs Basis-Stufenpläne"

    stufe = models.PositiveIntegerField(default=0, validators=[MinValueValidator(2)], unique=True)
    ep = models.PositiveIntegerField(default=0)

    ap = models.PositiveSmallIntegerField(default=0)
    fp = models.PositiveSmallIntegerField(default=0)
    fg = models.PositiveSmallIntegerField(default=0)
    tp = models.PositiveSmallIntegerField(default=0)

    def __str__(self):
        return "{} (EP: {})".format(self.stufe, self.ep)


class GfsAbility(models.Model):
    class Meta:
        ordering = ["name"]
        verbose_name = "Gfs-Fähigkeit"
        verbose_name_plural = "Gfs-Fähigkeiten"

    name = models.CharField(max_length=100, null=False, unique=True, verbose_name="Fähigkeit")
    beschreibung = models.TextField(max_length=2000, null=False, verbose_name="Beschreibung")

    needs_implementation = models.BooleanField(default=False)
    has_implementation = models.BooleanField(default=False, verbose_name="ist implementiert")
    has_choice = models.BooleanField(default=False)

    notizen = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.name


class GfsStufenplan(models.Model):
    class Meta:
        ordering = ['gfs', "basis"]
        verbose_name = "Stufenplan"
        verbose_name_plural = "Stufenpläne"
        unique_together = ["gfs", "basis"]

    gfs = models.ForeignKey(Gfs, on_delete=models.CASCADE)
    basis = models.ForeignKey(GfsStufenplanBase, on_delete=models.CASCADE, null=True)

    vorteile = models.ManyToManyField("Vorteil", blank=True)
    zauber = models.PositiveSmallIntegerField(default=0)
    wesenkräfte = models.ManyToManyField("Wesenkraft", blank=True)
    ability = models.OneToOneField(GfsAbility, on_delete=models.SET_NULL, null=True, blank=True)


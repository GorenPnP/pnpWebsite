from math import floor
import random, string

from datetime import date
import sys
from sentry_sdk import capture_message

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models.functions import Concat
from django.db.models import Max, Sum, FilteredRelation, Q, F, OuterRef, Subquery, Count
from django.shortcuts import get_object_or_404

from markdownfield.models import MarkdownField, RenderedMarkdownField
from markdownfield.validators import VALIDATOR_STANDARD

from log.create_log import logStufenaufstieg
from shop.models import *

from . import enums

class Spieler(models.Model):

    class Meta:
        ordering = ['name']
        verbose_name_plural = "Spieler"

    name = models.CharField(max_length=200, default='default')
    geburtstag = models.DateField(null=True, blank=True)

    def __str__(self):
        """ shown e.g. in dropdown as foreign key """
        return self.name

    def get_real_name(self):
        user = get_object_or_404(User, username=self.name)
        name = user.first_name
        if user.last_name:
            name += " " + user.last_name
        return name if name else user.username


class Wesenkraft(models.Model):
    class Meta:
        ordering = ['titel']
        verbose_name = "Wesenkraft"
        verbose_name_plural = "Wesenkräfte"

    titel = models.CharField(max_length=30, null=False, default="")
    probe = models.CharField(max_length=200, null=False, default="")
    wirkung = models.TextField(null=False, default="")
    manaverbrauch = models.CharField(max_length=100, null=True, blank=True, default="")
    min_rang = models.PositiveIntegerField(default=0)

    wesen = models.CharField(max_length=1, choices=enums.enum_wesenkr, null=False, default=enums.enum_wesenkr[0][0])
    zusatz_gfsspezifisch = models.ManyToManyField("Gfs", blank=True, related_name="zusatz_gfsspezifisch")
    zusatz_manifest = models.DecimalField('zusatz_manifest', max_digits=4, decimal_places=2,
                                          validators=[MaxValueValidator(10), MinValueValidator(0)], null=True, blank=True)

    def __str__(self):
        return "{} (Rang {})".format(self.titel, self.min_rang)


class Spezies(models.Model):

    class Meta:
        ordering = ['komplexität']
        verbose_name = "Wesen"
        verbose_name_plural = "Wesen"

    komplexität = models.PositiveIntegerField(default=0)
    titel = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return self.titel


class Gfs(models.Model):

    class Meta:
        ordering = ['titel']
        verbose_name = "Gfs/Klasse"
        verbose_name_plural = "Gfs/Klassen"

    DIFFICULTY_ENUM = [
        ("e", "für Einsteiger"),
        ("f", "für Fortgeschrittene"),
        ("p", "für Profis"),
    ]

    titel = models.CharField(max_length=30, unique=True)
    wesen = models.ForeignKey(Spezies, on_delete=models.SET_NULL, blank=True, null=True)
    beschreibung = MarkdownField(rendered_field='beschreibung_rendered', validator=VALIDATOR_STANDARD)
    beschreibung_rendered = RenderedMarkdownField(null=True)

    ap = models.PositiveIntegerField(default=0, validators=[MaxValueValidator(100)], verbose_name="AP-Kosten")

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
        return "{} ({})".format(self.titel, self.wesen.titel if self.wesen else "-")

    def relAttributQueryset(self):
        return GfsAttribut.objects.filter(gfs=self)

    def relVorteilQueryset(self):
        return GfsVorteil.objects.filter(gfs=self)

    def relNachteilQueryset(self):
        return GfsNachteil.objects.filter(gfs=self)


class Persönlichkeit(models.Model):
    
    class Meta:
        ordering = ['titel']
        verbose_name = "Persönlichkeit"
        verbose_name_plural = "Persönlichkeiten"

    titel = models.CharField(max_length=30, unique=True)
    positiv = models.TextField()
    negativ = models.TextField()

    def __str__(self):
        return self.titel


class Profession(models.Model):

    class Meta:
        ordering = ['titel']
        verbose_name = "Profession"
        verbose_name_plural = "Professionen"

    titel = models.CharField(max_length=30, unique=True)
    beschreibung = models.TextField(max_length=3000, blank=True, default='')

    attribute = models.ManyToManyField('Attribut', through='ProfessionAttribut')
    fertigkeiten = models.ManyToManyField("Fertigkeit", through="ProfessionFertigkeit")

    spezial = models.ManyToManyField("Spezialfertigkeit", through="ProfessionSpezialfertigkeit")
    wissen = models.ManyToManyField("Wissensfertigkeit", through="ProfessionWissensfertigkeit")

    def __str__(self):
        return self.titel

    def relAttributQueryset(self):
        return ProfessionAttribut.objects.filter(profession=self)


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
    pool = models.IntegerField(default=0)

    def __str__(self):
        return "'{}' von ’{}’".format(self.fertigkeit.__str__(), self.gfs.__str__())


class GfsWesenkraft(models.Model):

    class Meta:
        ordering = ['gfs', 'wesenkraft']
        verbose_name = "Wesenkraft"
        verbose_name_plural = "Wesenkräfte"

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

    anzahl = models.PositiveSmallIntegerField(default=1)
    notizen = models.CharField(max_length=100, default='', blank=True)

    attribut = models.ForeignKey("Attribut", on_delete=models.SET_NULL, null=True, blank=True)
    fertigkeit = models.ForeignKey("Fertigkeit", on_delete=models.SET_NULL, null=True, blank=True)
    engelsroboter = models.ForeignKey(Engelsroboter, on_delete=models.SET_NULL, null=True, blank=True)
    ip = models.PositiveSmallIntegerField(null=True, blank=True)


class GfsNachteil(models.Model):
    class Meta:
        ordering = ['teil']
        verbose_name = "Startnachteil"
        verbose_name_plural = "Startnachteile"
        unique_together = ["teil", "gfs"]

    teil = models.ForeignKey('Nachteil', on_delete=models.CASCADE)
    gfs = models.ForeignKey(Gfs, on_delete=models.CASCADE)

    anzahl = models.PositiveSmallIntegerField(default=1)
    notizen = models.CharField(max_length=100, default='', blank=True)

    attribut = models.ForeignKey("Attribut", on_delete=models.SET_NULL, null=True, blank=True)
    fertigkeit = models.ForeignKey("Fertigkeit", on_delete=models.SET_NULL, null=True, blank=True)
    engelsroboter = models.ForeignKey(Engelsroboter, on_delete=models.SET_NULL, null=True, blank=True)
    ip = models.PositiveSmallIntegerField(null=True, blank=True)


class ProfessionAttribut(models.Model):
    class Meta:
        ordering = ['attribut']
        verbose_name = "Startattribut"
        verbose_name_plural = "Startattribute"
        unique_together = ["attribut", "profession"]

    attribut = models.ForeignKey('Attribut', on_delete=models.CASCADE)
    profession = models.ForeignKey(Profession, on_delete=models.CASCADE)

    aktuellerWert = models.IntegerField(default=0)

    def __str__(self):
        return "'{}' von ’{}’".format(self.attribut.__str__(), self.profession.__str__())


class ProfessionFertigkeit(models.Model):

    class Meta:
        ordering = ['profession', 'fertigkeit']
        verbose_name = "Fertigkeit"
        verbose_name_plural = "Fertigkeiten"

        unique_together = (('profession', 'fertigkeit'),)

    profession = models.ForeignKey(Profession, on_delete=models.CASCADE)
    fertigkeit = models.ForeignKey("Fertigkeit", on_delete=models.CASCADE)

    fp = models.IntegerField(default=0)

    def __str__(self):
        return "'{}' von '{}'".format(self.fertigkeit.__str__(), self.profession.__str__())


class ProfessionSpezialfertigkeit(models.Model):

    class Meta:
        ordering = ['profession', 'spezial']
        verbose_name = "Startspezialfertigkeit"
        verbose_name_plural = "Startspezialfertigkeiten"

        unique_together = (('profession', 'spezial'),)

    profession = models.ForeignKey(Profession, on_delete=models.CASCADE)
    spezial = models.ForeignKey("Spezialfertigkeit", on_delete=models.CASCADE)

    def __str__(self):
        return "'{}' von '{}'".format(self.spezial.__str__(), self.profession.__str__())


class ProfessionWissensfertigkeit(models.Model):

    class Meta:
        ordering = ['profession', 'wissen']
        verbose_name = "Startwissensfertigkeit"
        verbose_name_plural = "Startwissensfertigkeiten"

        unique_together = (('profession', 'wissen'),)

    profession = models.ForeignKey(Profession, on_delete=models.CASCADE)
    wissen = models.ForeignKey("Wissensfertigkeit", on_delete=models.CASCADE)

    def __str__(self):
        return "'{}' von '{}'".format(self.wissen.__str__(), self.profession.__str__())


class GfsStufenplanBase(models.Model):
    class Meta:
        ordering = ["stufe"]
        verbose_name = "Gfs Basis-Stufenplan"
        verbose_name_plural = "Gfs Basis-Stufenpläne"
        unique_together = ["stufe"]

    stufe = models.PositiveIntegerField(default=0)
    ep = models.PositiveIntegerField(default=0)

    ap = models.PositiveSmallIntegerField(default=0)
    fp = models.PositiveSmallIntegerField(default=0)
    fg = models.PositiveSmallIntegerField(default=0)
    tp = models.PositiveSmallIntegerField(default=0)

    def __str__(self):
        return "{} (EP: {})".format(self.stufe, self.ep)


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
    special_ability = models.CharField(max_length=100, default=None, blank=True, null=True, verbose_name="Fähigkeit")
    special_ability_description = models.TextField(max_length=2000, default=None, blank=True, null=True, verbose_name="Beschreibung")


class ProfessionStufenplanBase(models.Model):
    class Meta:
        ordering = ["stufe"]
        verbose_name = "Profession Basis-Stufenplan"
        verbose_name_plural = "Profession Basis-Stufenpläne"
        unique_together = ["stufe"]

    stufe = models.PositiveIntegerField(default=0)
    ep = models.PositiveIntegerField(default=0)

    def __str__(self):
        return "{} (EP: {})".format(self.stufe, self.ep)


class ProfessionStufenplan(models.Model):
    class Meta:
        ordering = ['profession', "basis"]
        verbose_name = "Stufenplan"
        verbose_name_plural = "Stufenpläne"
        unique_together = ["profession", "basis"]

    profession = models.ForeignKey(Profession, on_delete=models.CASCADE)
    basis = models.ForeignKey(ProfessionStufenplanBase, on_delete=models.CASCADE, null=True)

    tp = models.PositiveSmallIntegerField(default=1)
    weiteres = models.TextField(max_length=1000, default=None, blank=True, null=True)


class Talent(models.Model):
    class Meta:
        ordering = ['titel']
        verbose_name = "Talent"
        verbose_name_plural = "Talente"
        unique_together = ["titel"]

    titel = models.CharField(max_length=200)
    tp = models.PositiveIntegerField(default=1)
    beschreibung = models.TextField()
    kategorie = models.CharField(max_length=1, choices=enums.talent_enum, default=enums.talent_enum[0][0])

    def __str__(self):
        return self.titel


class Religion(models.Model):
    class Meta:
        ordering = ['titel']
        verbose_name = "Religion"
        verbose_name_plural = "Religionen"
        unique_together = ["titel", "beschreibung"]

    titel = models.CharField(max_length=200)
    beschreibung = models.CharField(max_length=200, blank=True, default='')

    def __str__(self):
        return self.titel


class Teil(models.Model):
    """super for Vorteil, Nachteil"""
    class Meta:
        abstract = True
        ordering = ['titel', 'ip']
        unique_together = (('titel', 'ip', "beschreibung"),)

    titel = models.CharField(max_length=40)
    ip = models.PositiveIntegerField(default=0, validators=[MaxValueValidator(1000)])
    min_ip = models.PositiveIntegerField(default=0, validators=[MaxValueValidator(1000)])
    max_ip = models.PositiveIntegerField(default=0, validators=[MaxValueValidator(1000)])
    beschreibung = models.TextField(max_length=1000, blank=True, default="")

    wann_wählbar = models.CharField(max_length=1, choices=enums.teil_erstellung_enum, default=enums.teil_erstellung_enum[0][0])
    is_sellable = models.BooleanField(default=True)
    max_amount = models.PositiveSmallIntegerField(default=1, null=True, blank=True, help_text="Leer lassen für keine Beschränkung")

    needs_attribut = models.BooleanField(default=False)
    needs_fertigkeit = models.BooleanField(default=False)
    needs_engelsroboter = models.BooleanField(default=False)
    needs_notiz = models.BooleanField(default=False)
    needs_ip = models.BooleanField(default=False)


class Vorteil(Teil):

    class Meta:
        verbose_name_plural = "Vorteile"
        verbose_name = "Vorteil"

    def __str__(self):
        return "{} (kostet {} IP)".format(self.titel, self.ip)


class Nachteil(Teil):

    class Meta:
        verbose_name_plural = "Nachteile"
        verbose_name = "Nachteil"

    def __str__(self):
        return "{} (gibt {} IP)".format(self.titel, self.ip)


class Attribut(models.Model):

    class Meta:
        ordering = ['id']
        verbose_name = "Attribut"
        verbose_name_plural = "Attribute"

    titel = models.CharField(max_length=3, unique=True)
    beschreibung = models.CharField(max_length=100, blank=True, default='')

    def __str__(self):
        return "{}".format(self.titel)


class Beruf(models.Model):

    class Meta:
        ordering = ['titel']
        verbose_name = "Beruf"
        verbose_name_plural = "Berufe"

    titel = models.CharField(max_length=200, unique=True)
    beschreibung = models.CharField(max_length=100, blank=True, default='')

    def __str__(self):
        return self.titel


class Fertigkeit(models.Model):

    class Meta:
        ordering = ['id']
        verbose_name = "Fertigkeit"
        verbose_name_plural = "Fertigkeiten"

    titel = models.CharField(max_length=50, unique=True)
    attr1 = models.ForeignKey(Attribut, null=True, on_delete=models.SET_NULL, related_name="attr1")
    attr2 = models.ForeignKey(Attribut, on_delete=models.SET_NULL, related_name="attr2", blank=True, null=True)
    limit = models.CharField(choices=enums.limit_enum, max_length=20, default=enums.limit_enum[0])
    beschreibung = models.CharField(max_length=100, blank=True, default='')

    def __str__(self):
        if self.attr2 is None:
            return "{} ({})".format(self.titel, self.attr1)
        else:
            return "{} ({}, {})".format(self.titel, self.attr1, self.attr2)

    def clean(self):
        if self.attr1 is None and self.attr2 is not None:
            raise ValidationError("Erstes Attribut wählen, wenn nur eins gebraucht wird!")


class Wissensfertigkeit(models.Model):

    class Meta:
        verbose_name = "Wissensfertigkeit"
        verbose_name_plural = "Wissensfertigkeiten"
        ordering = ['titel']

    titel = models.CharField(max_length=200, unique=True)
    attr1 = models.ForeignKey(Attribut, null=True, on_delete=models.SET_NULL, related_name="a1")
    attr2 = models.ForeignKey(Attribut, null=True, on_delete=models.SET_NULL, related_name="a2")
    attr3 = models.ForeignKey(Attribut, null=True, on_delete=models.SET_NULL, related_name="a3")
    fertigkeit = models.ManyToManyField(Fertigkeit)
    beschreibung = models.CharField(max_length=100, blank=True, default='')

    def __str__(self):
        st = self.attr1.__str__()
        nd = self.attr2.__str__()
        rd = self.attr3.__str__()
        return "{} ({}, {}, {})".format(self.titel, st, nd, rd)


class Spezialfertigkeit(models.Model):

    class Meta:
        verbose_name_plural = "Spezialfertigkeiten"
        verbose_name = "Spezialfertigkeit"
        ordering = ['titel']

    titel = models.CharField(max_length=200, unique=True)
    attr1 = models.ForeignKey(Attribut, null=True, on_delete=models.SET_NULL, related_name="attribut1")
    attr2 = models.ForeignKey(Attribut, null=True, on_delete=models.SET_NULL, related_name="attribut2")
    ausgleich = models.ManyToManyField(Fertigkeit)
    beschreibung = models.CharField(max_length=100, blank=True, default='')

    def __str__(self):
        st = self.attr1.__str__()
        nd = self.attr2.__str__()
        return "{} ({}, {})".format(self.titel, st, nd)


# default for Charakter.name
def rand_str():
    return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(10))


class Charakter(models.Model):

    class Meta:
        verbose_name = "Charakter"
        verbose_name_plural = "Charaktere"
        ordering = ["eigentümer", 'name']

    in_erstellung = models.BooleanField(default=True)
    ep_system = models.BooleanField(default=True)
    larp = models.BooleanField(default=False)

    eigentümer = models.ForeignKey(Spieler, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=200, null=True, blank=True)
    spezies = models.ManyToManyField(Spezies, related_name='wesen', through='character.RelSpezies')
    gfs = models.ForeignKey(Gfs, on_delete=models.SET_NULL, null=True, blank=True)
    profession = models.ForeignKey(Profession, on_delete=models.SET_NULL, null=True, blank=True)

    manifest = models.DecimalField('Startmanifest', max_digits=4, decimal_places=2, default=10.0,
                                   validators=[MaxValueValidator(10), MinValueValidator(0)])
    sonstiger_manifestverlust = models.DecimalField("sonstiger Manifestverlust", max_digits=4, decimal_places=2, default=0.0,
                                                    validators=[MaxValueValidator(10), MinValueValidator(0)], blank=True)
    notizen_sonstiger_manifestverlust = models.CharField(max_length=200, default="", blank=True)

    gewicht = models.PositiveIntegerField(default=75, blank=True, verbose_name="Gewicht in kg")
    größe = models.PositiveIntegerField(default=170, blank=True, verbose_name="Größe in cm")
    alter = models.PositiveIntegerField(default=0, blank=True)
    geschlecht = models.CharField(max_length=100, blank=True)
    sexualität = models.CharField(max_length=100, blank=True)
    beruf = models.ForeignKey(Beruf, null=True, on_delete=models.SET_NULL, blank=True)
    präf_arm = models.CharField(max_length=100, default="", blank=True, verbose_name="präferierter Arm (rechts/links?)")
    religion = models.ForeignKey(Religion, null=True, on_delete=models.SET_NULL, blank=True)
    hautfarbe = models.CharField(max_length=100, default="", blank=True)
    haarfarbe = models.CharField(max_length=100, default="", blank=True)
    augenfarbe = models.CharField(max_length=100, default="", blank=True)

    nutzt_magie = models.PositiveSmallIntegerField(choices=enums.nutzt_magie_enum, default=enums.nutzt_magie_enum[0][0], blank=True)

    ap = models.PositiveIntegerField(null=True, blank=True)
    fp = models.PositiveIntegerField(null=True, blank=True)
    fg = models.PositiveIntegerField(null=True, blank=True)
    sp = models.PositiveIntegerField(null=True, blank=True)
    ip = models.IntegerField(null=True, blank=True)
    tp = models.IntegerField(null=True, blank=True)
    spF_wF = models.IntegerField(null=True, blank=True)
    wp = models.IntegerField(null=True, blank=True)
    zauberplätze = models.JSONField(null=True, blank=True) # {"0": 2, "2": 1}
    geld = models.IntegerField(default=0)
    konzentration = models.PositiveSmallIntegerField(null=True, blank=True)
    prestige = models.PositiveIntegerField(default=0)
    verzehr = models.PositiveIntegerField(default=0)

    ep = models.PositiveIntegerField(default=0)
    ep_stufe = models.PositiveIntegerField(default=0)
    ep_stufe_in_progress = models.PositiveIntegerField(default=0)

    HPplus = models.IntegerField(default=0, blank=True)
    HPplus_fix = models.IntegerField(default=None, null=True, blank=True)
    wesenschaden_waff_kampf = models.IntegerField(default=0)
    wesenschaden_andere_gestalt = models.IntegerField("BS andere Gestalt", blank=True, null=True)
    rang = models.PositiveIntegerField(default=0, validators=[MaxValueValidator(500)], blank=True)

    vorteile = models.ManyToManyField(Vorteil, through="character.RelVorteil", blank=True)
    nachteile = models.ManyToManyField(Nachteil, through="character.RelNachteil", blank=True)
    talente = models.ManyToManyField(Talent, through="character.RelTalent", blank=True)

    notizen = models.TextField(blank=True)
    persönlicheZiele = models.TextField(blank=True)

    persönlichkeit = models.ManyToManyField(Persönlichkeit, blank=True)
    wesenkräfte = models.ManyToManyField(Wesenkraft, through="character.RelWesenkraft", blank=True)

    attribute = models.ManyToManyField(Attribut, through="character.RelAttribut", blank=True)
    fertigkeiten = models.ManyToManyField(Fertigkeit, through='character.RelFertigkeit', blank=True)
    spezialfertigkeiten = models.ManyToManyField(Spezialfertigkeit, through='character.RelSpezialfertigkeit', blank=True)
    wissensfertigkeiten = models.ManyToManyField(Wissensfertigkeit, through='character.RelWissensfertigkeit', blank=True)

    items = models.ManyToManyField(Item, through='character.RelItem', blank=True)
    waffenWerkzeuge = models.ManyToManyField(Waffen_Werkzeuge, through='character.RelWaffen_Werkzeuge', blank=True)
    magazine = models.ManyToManyField(Magazin, through='character.RelMagazin', blank=True)
    schusswaffen = models.ManyToManyField(Schusswaffen, through='character.RelSchusswaffen', blank=True)
    magischeAusrüstung = models.ManyToManyField(Magische_Ausrüstung, through='character.RelMagische_Ausrüstung', blank=True)
    rituale_runen = models.ManyToManyField(Rituale_Runen, through='character.RelRituale_Runen', blank=True)
    rüstungen = models.ManyToManyField(Rüstungen, through='character.RelRüstung', blank=True)
    ausrüstungTechnik = models.ManyToManyField(Ausrüstung_Technik, through='character.RelAusrüstung_Technik', blank=True)
    fahrzeuge = models.ManyToManyField(Fahrzeug, through='character.RelFahrzeug', blank=True)
    einbauten = models.ManyToManyField(Einbauten, through='character.RelEinbauten', blank=True)
    zauber = models.ManyToManyField(Zauber, through='character.RelZauber', blank=True)
    vergessene_zauber = models.ManyToManyField(VergessenerZauber, through='character.RelVergessenerZauber', blank=True)
    begleiter = models.ManyToManyField(Begleiter, through='character.RelBegleiter', blank=True)
    engelsroboter = models.ManyToManyField(Engelsroboter, through='character.RelEngelsroboter', blank=True)

    sonstige_items = models.TextField(max_length=1000, default='', blank=True)

    def __str__(self):
        return "{} ({})".format(self.name, self.eigentümer)

    def HP_plus_(self):
        return self.HPplus

    def get_konzentration(self):
        return self.konzentration if self.konzentration is not None else RelAttribut.objects.get(char=self, attribut__titel="IN").aktuell() * 5

    def get_max_stufe(self) -> int:
        return GfsStufenplanBase.objects.filter(ep__lte=self.ep).aggregate(Max("stufe"))["stufe__max"] or 0

    def max_tier_allowed(self) -> int:
        return min(1 + floor(self.ep_stufe_in_progress / 4), 7)

    def init_stufenhub(self):
        max_stufe = self.get_max_stufe()
        if self.ep_stufe_in_progress >= max_stufe or self.gfs is None: return

        base_qs = self.gfs.gfsstufenplan_set\
            .prefetch_related("basis")\
            .filter(basis__stufe__gt=self.ep_stufe_in_progress or self.ep_stufe, basis__stufe__lte=max_stufe)

        # numeric values
        numeric_values = base_qs\
            .aggregate(
                ap=Sum("basis__ap"),
                fp=Sum("basis__fp"),
                fg=Sum("basis__fg"),
            )


        # vorteile
        vorteil_ids = base_qs.filter(vorteile__isnull=False).values_list("vorteile__id", flat=True)
        vorteile = Vorteil.objects.filter(id__in=vorteil_ids)
        rel_vorteile = RelVorteil.objects\
            .filter(char=self, teil__in=vorteile)\
            .values("teil__id", "anzahl")

        for vorteil_id in set(vorteil_ids):
            vorteil = vorteile.get(id=vorteil_id)
            sum_rel_vorteile = len([x for x in rel_vorteile if x["teil__id"] == vorteil_id])
            sum_vorteile = len([x for x in vorteil_ids if x == vorteil_id])
            total_sum = sum_rel_vorteile + sum_vorteile
            max_amount = vorteil.max_amount if vorteil.max_amount is not None else sys.maxsize

            # some not allowed, give ip
            amount_in_overflow = total_sum - max_amount
            if amount_in_overflow > 0:
                print(amount_in_overflow, "x", f"Will give you {vorteil.ip} IP for ", vorteil.titel)
                self.ip += amount_in_overflow * vorteil.ip

            # needs more information
            amount_to_create = min(max_amount - sum_rel_vorteile, sum_vorteile)
            if max_amount != 1 and amount_to_create > 0:
                print(amount_to_create, "x", "create RelVorteil for", vorteil.titel)
                for _ in range(amount_to_create):
                    RelVorteil.objects.create(teil=vorteil, char=self, anzahl=1, will_create=True)

        # persist
        self.ap += numeric_values["ap"]
        self.fp += numeric_values["fp"]
        self.fg += numeric_values["fg"]
        self.ep_stufe_in_progress = max_stufe
        
        logStufenaufstieg(self.eigentümer, self)
        print("alte Stufe", self.ep_stufe, "Neue Stufe", max_stufe)

        self.save(update_fields=["ap", "fp", "fg", "ip", "ep_stufe_in_progress"])

    def submit_stufenhub(self):
        if self.ep_stufe >= self.ep_stufe_in_progress or self.gfs is None: return

        base_qs = self.gfs.gfsstufenplan_set\
            .prefetch_related("basis")\
            .filter(basis__stufe__gt=self.ep_stufe, basis__stufe__lte=self.ep_stufe_in_progress)

        # tp (numeric values)
        self.tp += base_qs.aggregate(tp=Sum("basis__tp"))["tp"]

        # zauber
        for plan in base_qs.filter(zauber__gt=0):
            for _ in range(plan.zauber):
                self.zauberplätze.append(plan.basis.stufe)

        # wesenkräfte
        wesenkräfte = base_qs.filter(wesenkräfte__isnull=False).wesenkräfte
        for w in wesenkräfte:
            _, created = RelWesenkraft.objects.get_or_create(char=self, wesenkraft=w, defaults={"tier": 1 if w.wesen == "w" and self.gfs in w.zusatz_gfsspezifisch else 0})
            if not created:
                # log that wesenkraft already existed
                print(f"Wesenkraft {w.titel} war bei {self.name} ({self.gfs.titel}) im EP-Tree Stufe {self.ep_stufe+1} - {self.ep_stufe_in_progress}")
                capture_message(f"Wesenkraft {w.titel} war bei {self.name} ({self.gfs.titel}) im EP-Tree Stufe {self.ep_stufe+1} - {self.ep_stufe_in_progress}", level='info')

        # vorteile
        new_vorteil = base_qs.filter(vorteile__isnull=False)
        rel_vorteil = RelVorteil.objects\
            .filter(char=self, teil__id__in=[v["id"] for v in vorteile])\
            .values_list("teil", flat=True)

        vorteile = Vorteil.objects\
            .filter(id__in=new_vorteil, max_amount=1)\
            .exclude(id__in=rel_vorteil)

        for vorteil in vorteile:
            # add vorteil. No extra information needed.
            print("1x add on submit of Stufe", vorteil.titel)
            RelVorteil.objects.create(char=self, teil=vorteil)

        self.ep_stufe = self.ep_stufe_in_progress
        self.save(update_fields=["tp", "zauberplätze", "ep_stufe"])


class RelWesenkraft(models.Model):

    class Meta:
        ordering = ['char', 'wesenkraft']
        verbose_name = "Wesenkraft"
        verbose_name_plural = "Wesenkräfte"

        unique_together = (('char', 'wesenkraft'),)

    char = models.ForeignKey(Charakter, on_delete=models.CASCADE)
    wesenkraft = models.ForeignKey(Wesenkraft, on_delete=models.CASCADE)

    def __str__(self):
        return "'{}' von Charakter '{}'".format(self.wesenkraft, self.char)


class Affektivität(models.Model):

    class Meta:
        ordering = ['char', 'name']
        verbose_name = "Affektivität"
        verbose_name_plural = "Affektivitäten"

        unique_together = (('char', 'name'),)

    char = models.ForeignKey(Charakter, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    wert = models.IntegerField(default=0, validators=[MinValueValidator(-200), MaxValueValidator(200)])
    notizen = models.CharField(max_length=100, blank=True, default='')

    def __str__(self):
        return "'{}' zu Charakter '{}'".format(self.name, self.char)


class RelSpezies(models.Model):
    class Meta:
        ordering = ['char', 'spezies']
        verbose_name = "Wesen"
        verbose_name_plural = "Wesen"

        unique_together = (('char', 'spezies'),)

    char = models.ForeignKey(Charakter, on_delete=models.CASCADE)
    spezies = models.ForeignKey(Spezies, on_delete=models.CASCADE, related_name="Wesen")

    def __str__(self):
        return "Charakter '{}' ist ein/e '{}'".format(self.char.name, self.spezies.titel)


class RelPersönlichkeit(models.Model):
    class Meta:
        ordering = ['char', 'persönlichkeit']
        verbose_name = "Persönlichkeit"
        verbose_name_plural = "Persönlichkeiten"

        unique_together = (('char', 'persönlichkeit'),)

    char = models.ForeignKey(Charakter, on_delete=models.CASCADE)
    persönlichkeit = models.ForeignKey(Persönlichkeit, on_delete=models.CASCADE)

    def __str__(self):
        return "Charakter '{}' ist '{}'".format(self.char.name, self.persönlichkeit.titel)


class RelTalent(models.Model):
    class Meta:
        ordering = ['char', 'talent']
        verbose_name = "Talent"
        verbose_name_plural = "Talente"

        unique_together = (('char', 'talent'),)

    char = models.ForeignKey(Charakter, on_delete=models.CASCADE)
    talent = models.ForeignKey(Talent, on_delete=models.CASCADE)

    def __str__(self):
        return "{} von {}".format(self.talent.titel, self.char.name)


class RelTeil(models.Model):
    """super for RelVorteil, RelNachteil"""
    class Meta:
        abstract = True
        ordering = ['char', 'teil']

        unique_together = (('char', 'teil', "extra", "notizen"),)

    char = models.ForeignKey(Charakter, on_delete=models.CASCADE)
    teil = None

    anzahl = models.PositiveSmallIntegerField(default=1)
    notizen = models.CharField(max_length=500, blank=True, null=True)

    attribut = models.ForeignKey(Attribut, on_delete=models.SET_NULL, null=True, blank=True)
    fertigkeit = models.ForeignKey(Fertigkeit, on_delete=models.SET_NULL, null=True, blank=True)
    engelsroboter = models.ForeignKey(Engelsroboter, on_delete=models.SET_NULL, null=True, blank=True)
    ip = models.PositiveSmallIntegerField(null=True, blank=True)

    def __str__(self):
        return "'{}' zu Charakter '{}'".format(self.teil.titel, self.char.name)


class RelVorteil(RelTeil):
    class Meta:
        verbose_name = "Vorteil"
        verbose_name_plural = "Vorteile"

    teil = models.ForeignKey(Vorteil, on_delete=models.CASCADE)

    will_create = models.BooleanField(default=False)


class RelNachteil(RelTeil):
    class Meta:
        verbose_name = "Nachteil"
        verbose_name_plural = "Nachteile"

    teil = models.ForeignKey(Nachteil, on_delete=models.CASCADE)


class RelAttribut(models.Model):

    class Meta:
        ordering = ['char', 'attribut']
        verbose_name = "Attribut"
        verbose_name_plural = "Attribute"

        unique_together = (('char', 'attribut'),)

    char = models.ForeignKey(Charakter, on_delete=models.CASCADE)
    attribut = models.ForeignKey(Attribut, on_delete=models.CASCADE)

    aktuellerWert = models.PositiveIntegerField(default=0)
    aktuellerWert_temp = models.PositiveIntegerField(default=0)
    aktuellerWert_bonus = models.PositiveIntegerField(default=0)
    aktuellerWert_fix = models.PositiveIntegerField(null=True, blank=True)

    maxWert = models.PositiveIntegerField(default=0)
    maxWert_temp = models.PositiveIntegerField(default=0)
    maxWert_bonus = models.PositiveIntegerField(default=0)
    maxWert_fix = models.PositiveIntegerField(null=True, blank=True)

    fg = models.PositiveIntegerField(default=0)
    fg_temp = models.PositiveIntegerField(default=0)
    fg_bonus = models.PositiveIntegerField(default=0)

    def __str__(self):
        return "'{}' von '{}'".format(self.attribut.__str__(), self.char.__str__())

    def aktuell(self): return self.aktuellerWert + self.aktuellerWert_temp + self.aktuellerWert_bonus
    def max(self): return self.maxWert + self.maxWert_temp + self.maxWert_bonus
    def fg_sum(self): return self.fg + self.fg_temp + self.fg_bonus

class RelFertigkeit(models.Model):

    class Meta:
        ordering = ['char', 'fertigkeit']
        verbose_name = "Fertigkeit"
        verbose_name_plural = "Fertigkeiten"

        unique_together = (('char', 'fertigkeit'),)

    char = models.ForeignKey(Charakter, on_delete=models.CASCADE)
    fertigkeit = models.ForeignKey(Fertigkeit, on_delete=models.CASCADE)

    fp = models.SmallIntegerField(default=0)
    fp_temp = models.SmallIntegerField(default=0)
    fp_bonus = models.SmallIntegerField(default=0)

    def __str__(self):
        return "'{}' von '{}'".format(self.fertigkeit.__str__(), self.char.__str__())

    def pool(self):
        pool = self.fp + self.fp_temp + self.fp_bonus
        relAttr1 = RelAttribut.objects.get(char=self.char, attribut=self.fertigkeit.attr1)
        pool += relAttr1.aktuell()

        if (self.fertigkeit.attr2):
            relAttr2 = RelAttribut.objects.get(char=self.char, attribut=self.fertigkeit.attr2)
            pool += relAttr2.aktuell()
        else:
            pool += relAttr1.fg_sum()

        return pool


class RelWissensfertigkeit(models.Model):

    class Meta:
        ordering = ['char', 'wissensfertigkeit']
        verbose_name = "Wissensfertigkeit"
        verbose_name_plural = "Wissensfertigkeiten"

        unique_together = (('char', 'wissensfertigkeit'),)

    char = models.ForeignKey(Charakter, on_delete=models.CASCADE)
    wissensfertigkeit = models.ForeignKey(Wissensfertigkeit, on_delete=models.CASCADE)

    würfel2 = models.SmallIntegerField(choices=enums.würfelart_enum, default=enums.würfelart_enum[0][0])

    def __str__(self):
        return "'{}' von ’{}’".format(self.wissensfertigkeit.__str__(), self.char.__str__())


class RelSpezialfertigkeit(models.Model):
    class Meta:
        ordering = ['char', 'spezialfertigkeit']
        verbose_name = "Spezialfertigkeit"
        verbose_name_plural = "Spezialfertigkeiten"

        unique_together = (('char', 'spezialfertigkeit'),)

    char = models.ForeignKey(Charakter, on_delete=models.CASCADE)
    spezialfertigkeit = models.ForeignKey(Spezialfertigkeit, on_delete=models.CASCADE)

    stufe = models.PositiveIntegerField(default=0, validators=[MaxValueValidator(50)])

    def __str__(self):
        return "'{}' von ’{}’".format(self.spezialfertigkeit.__str__(), self.char.__str__())


############ RelShop ###########

class RelShop(models.Model):
    class Meta:
        abstract = True
        ordering = ['char', 'item']
        unique_together = (('char', 'item', "notizen"),)

    char = models.ForeignKey(Charakter, on_delete=models.CASCADE)
    anz = models.PositiveIntegerField(default=1)
    stufe = models.PositiveIntegerField(default=None, null=True)
    notizen = models.CharField(max_length=50, blank=True, default='')

    def __str__(self):
        return "{} ({})".format(self.item, self.anz)


class RelItem(RelShop):
    class Meta:
        verbose_name = "Item"
        verbose_name_plural = "Items"

    item = models.ForeignKey(Item, on_delete=models.CASCADE)


class RelWaffen_Werkzeuge(RelShop):
    class Meta:
        verbose_name = "Waffe/Werkzeug"
        verbose_name_plural = "Waffen & Werkzeuge"

    item = models.ForeignKey(Waffen_Werkzeuge, on_delete=models.CASCADE)


class RelMagazin(RelShop):
    class Meta:
        verbose_name = "Magazin"
        verbose_name_plural = "Magazine"

    item = models.ForeignKey(Magazin, on_delete=models.CASCADE)


class RelPfeil_Bolzen(RelShop):
    class Meta:
        verbose_name = "Pfeil/Bolzen"
        verbose_name_plural = "Pfeile & Bolzen"

    item = models.ForeignKey(Pfeil_Bolzen, on_delete=models.CASCADE)


class RelSchusswaffen(RelShop):
    class Meta:
        verbose_name = "Schusswaffe"
        verbose_name_plural = "Schusswaffen"

    item = models.ForeignKey(Schusswaffen, on_delete=models.CASCADE)


class RelMagische_Ausrüstung(RelShop):
    class Meta:
        verbose_name = "magische Ausrüstung"
        verbose_name_plural = "magische Ausrüstung"

    item = models.ForeignKey(Magische_Ausrüstung, on_delete=models.CASCADE)


class RelRüstung(RelShop):
    class Meta:
        verbose_name = "Rüstung"
        verbose_name_plural = "Rüstungen"

    item = models.ForeignKey(Rüstungen, on_delete=models.CASCADE)


class RelAusrüstung_Technik(RelShop):
    class Meta:
        verbose_name = "Ausrüstung & Technik"
        verbose_name_plural = "Ausrüstung & Technik"

    item = models.ForeignKey(Ausrüstung_Technik, on_delete=models.CASCADE)
    selbst_eingebaut = models.BooleanField(default=False)


class RelFahrzeug(RelShop):
    class Meta:
        verbose_name = "Fahrzeug"
        verbose_name_plural = "Fahrzeuge"

    item = models.ForeignKey(Fahrzeug, on_delete=models.CASCADE)


class RelEinbauten(RelShop):
    class Meta:
        verbose_name = "Einbauten"
        verbose_name_plural = "Einbauten"

    item = models.ForeignKey(Einbauten, on_delete=models.CASCADE)


class RelZauber(RelShop):
    class Meta:
        verbose_name = "Zauber"
        verbose_name_plural = "Zauber"

    item = models.ForeignKey(Zauber, on_delete=models.CASCADE)

    # tier
    tier = models.PositiveSmallIntegerField(default=0, validators=[MaxValueValidator(7)])
    tier_notes = models.JSONField(default=dict, blank=True)

    def __str__(self):
        return "{}".format(self.item)


class RelVergessenerZauber(RelShop):
    class Meta:
        verbose_name = "vergessener Zauber"
        verbose_name_plural = "vergessene Zauber"

    item = models.ForeignKey(VergessenerZauber, on_delete=models.CASCADE)

    def __str__(self):
        return "{}".format(self.item)


class RelAlchemie(RelShop):
    class Meta:
        verbose_name = "Alchemie"
        verbose_name_plural = "Alchemie"

    item = models.ForeignKey(Alchemie, on_delete=models.CASCADE)


class RelTinker(RelShop):
    class Meta:
        verbose_name = "Für Selbstständige"
        verbose_name_plural = "Für Selbstständige"

    item = models.ForeignKey(Tinker, on_delete=models.CASCADE)


class RelBegleiter(RelShop):
    class Meta:
        verbose_name = "Begleiter"
        verbose_name_plural = "Begleiter"

    item = models.ForeignKey(Begleiter, on_delete=models.CASCADE, null=True)


class RelEngelsroboter(RelShop):
    class Meta:
        verbose_name = "Engelsroboter"
        verbose_name_plural = "Engelsroboter"

    item = models.ForeignKey(Engelsroboter, on_delete=models.CASCADE, null=True)


class RelRituale_Runen(RelShop):
    class Meta:
        verbose_name = "Ritual/Rune"
        verbose_name_plural = "Rituale & Runen"

    item = models.ForeignKey(Rituale_Runen, on_delete=models.CASCADE)


# verf_shop_firma
############ RelShop ###########
class RelFirmaShop(models.Model):
    class Meta:
        abstract = True
        ordering = ['char', 'firma_shop']
        unique_together = (('char', "firma_shop"),)

    char = models.ForeignKey(Charakter, on_delete=models.CASCADE)
    last_tried = models.DateField(default=date.today)

    def __str__(self):
        return "{}, {}, {}".format(self.firma_shop, self.char, self.last_tried)


class RelFirmaItem(RelFirmaShop):
    class Meta:
        verbose_name = "Item Verfügbarkeit"
        verbose_name_plural = "Items Verfügbarkeiten"

    firma_shop = models.ForeignKey(FirmaItem, on_delete=models.CASCADE)


class RelFirmaWaffen_Werkzeuge(RelFirmaShop):
    class Meta:
        verbose_name = "Waffe/Werkzeug Verfügbarkeit"
        verbose_name_plural = "Waffen & Werkzeuge Verfügbarkeiten"

    firma_shop = models.ForeignKey(FirmaWaffen_Werkzeuge, on_delete=models.CASCADE)


class RelFirmaMagazin(RelFirmaShop):
    class Meta:
        verbose_name = "Magazin Verfügbarkeit"
        verbose_name_plural = "Magazine Verfügbarkeiten"

    firma_shop = models.ForeignKey(FirmaMagazin, on_delete=models.CASCADE)


class RelFirmaPfeil_Bolzen(RelFirmaShop):
    class Meta:
        verbose_name = "Pfeil/Bolzen Verfügbarkeit"
        verbose_name_plural = "Pfeile & Bolzen Verfügbarkeiten"

    firma_shop = models.ForeignKey(FirmaPfeil_Bolzen, on_delete=models.CASCADE)


class RelFirmaSchusswaffen(RelFirmaShop):
    class Meta:
        verbose_name = "Schusswaffe Verfügbarkeit"
        verbose_name_plural = "Schusswaffen Verfügbarkeiten"

    firma_shop = models.ForeignKey(FirmaSchusswaffen, on_delete=models.CASCADE)


class RelFirmaMagische_Ausrüstung(RelFirmaShop):
    class Meta:
        verbose_name = "magische Ausrüstung Verfügbarkeit"
        verbose_name_plural = "magische Ausrüstung Verfügbarkeiten"

    firma_shop = models.ForeignKey(FirmaMagische_Ausrüstung, on_delete=models.CASCADE)


class RelFirmaRüstung(RelFirmaShop):
    class Meta:
        verbose_name = "Rüstung Verfügbarkeit"
        verbose_name_plural = "Rüstungen Verfügbarkeiten"

    firma_shop = models.ForeignKey(FirmaRüstungen, on_delete=models.CASCADE)


class RelFirmaAusrüstung_Technik(RelFirmaShop):
    class Meta:
        verbose_name = "Ausrüstung & Technik Verfügbarkeit"
        verbose_name_plural = "Ausrüstung & Technik Verfügbarkeiten"

    firma_shop = models.ForeignKey(FirmaAusrüstung_Technik, on_delete=models.CASCADE)


class RelFirmaFahrzeug(RelFirmaShop):
    class Meta:
        verbose_name = "Fahrzeug Verfügbarkeit"
        verbose_name_plural = "Fahrzeuge Verfügbarkeiten"

    firma_shop = models.ForeignKey(FirmaFahrzeug, on_delete=models.CASCADE)


class RelFirmaEinbauten(RelFirmaShop):
    class Meta:
        verbose_name = "Einbauten Verfügbarkeit"
        verbose_name_plural = "Einbauten Verfügbarkeiten"

    firma_shop = models.ForeignKey(FirmaEinbauten, on_delete=models.CASCADE)


class RelFirmaZauber(RelFirmaShop):
    class Meta:
        verbose_name = "Zauber Verfügbarkeit"
        verbose_name_plural = "Zauber Verfügbarkeiten"

    firma_shop = models.ForeignKey(FirmaZauber, on_delete=models.CASCADE)

    def __str__(self):
        return "{}".format(self.firma_shop)


class RelFirmaVergessenerZauber(RelFirmaShop):
    class Meta:
        verbose_name = "vergessener Zauber Verfügbarkeit"
        verbose_name_plural = "vergessener Zauber Verfügbarkeiten"

    firma_shop = models.ForeignKey(FirmaVergessenerZauber, on_delete=models.CASCADE)

    def __str__(self):
        return "{}".format(self.firma_shop)


class RelFirmaAlchemie(RelFirmaShop):
    class Meta:
        verbose_name = "Alchemie Verfügbarkeit"
        verbose_name_plural = "Alchemie Verfügbarkeiten"

    firma_shop = models.ForeignKey(FirmaAlchemie, on_delete=models.CASCADE)


class RelFirmaTinker(RelFirmaShop):
    class Meta:
        verbose_name = "Für Selbstständige Verfügbarkeit"
        verbose_name_plural = "Für Selbstständige Verfügbarkeiten"

    firma_shop = models.ForeignKey(FirmaTinker, on_delete=models.CASCADE)


class RelFirmaBegleiter(RelFirmaShop):
    class Meta:
        verbose_name = "Begleiter Verfügbarkeit"
        verbose_name_plural = "Begleiter Verfügbarkeiten"

    firma_shop = models.ForeignKey(FirmaBegleiter, on_delete=models.CASCADE)


class RelFirmaEngelsroboter(RelFirmaShop):
    class Meta:
        verbose_name = "Engelsroboter Verfügbarkeit"
        verbose_name_plural = "Engelsroboter Verfügbarkeiten"

    firma_shop = models.ForeignKey(FirmaEngelsroboter, on_delete=models.CASCADE)


class RelFirmaRituale_Runen(RelFirmaShop):
    class Meta:
        verbose_name = "Ritual/Rune Verfügbarkeit"
        verbose_name_plural = "Rituale & Runen Verfügbarkeiten"

    firma_shop = models.ForeignKey(FirmaRituale_Runen, on_delete=models.CASCADE)

# bonus things
class SkilltreeBase(models.Model):
    class Meta:
        unique_together = ["kind", "stufe"]

    kind = models.CharField(max_length=1, choices=enums.skilltreeBase_enum, null=True)

    # stufe == 0: Bonus
    stufe = models.PositiveIntegerField(validators=[MaxValueValidator(10)], default=1)
    sp = models.PositiveIntegerField(default=1)

    def __str__(self):
        return "{} (Stufe {}, {} SP)".format(self.get_kind_display(), self.stufe, self.sp)


class SkilltreeEntryGfs(models.Model):
    class Meta:
        unique_together = ["context", "gfs"]

    context = models.ForeignKey(SkilltreeBase, on_delete=models.CASCADE)

    gfs = models.ForeignKey(Gfs, on_delete=models.CASCADE)
    text = models.TextField(max_length=100, null=True)

    def __str__(self):
        return "{} (Stufe {})".format(self.gfs, self.context.stufe)


class SkilltreeEntryProfession(models.Model):
    class Meta:
        unique_together = ["context", "profession"]

    context = models.ForeignKey(SkilltreeBase, on_delete=models.CASCADE)

    profession = models.ForeignKey(Profession, on_delete=models.CASCADE)
    text = models.TextField(max_length=100, null=True)

    def __str__(self):
        return "{} (Stufe {})".format(self.profession, self.context.stufe)


class SkilltreeEntryKategorie(models.Model):
    class Meta:
        unique_together = ["context", "kategorie"]

    context = models.ForeignKey(SkilltreeBase, on_delete=models.CASCADE, null=True)

    kategorie = models.CharField(max_length=2, choices=enums.skilltree_kategorie_enum, null=True)
    text = models.TextField(max_length=100)

    def __str__(self):
        return "{}, {} (Stufe {})".format(self.context.get_kind_display(), self.get_kategorie_display(), self.context.stufe)


class RangRankingEntry(models.Model):
    class Meta:
        ordering = ["order"]

    order = models.PositiveIntegerField(default=0, primary_key=True)
    ranking = models.CharField(max_length=3, default="Z")
    min_rang = models.CharField(max_length=10, default="0")
    max_rang = models.CharField(max_length=10, default="49")

    survival = models.CharField(max_length=100, null=True, blank=True)
    power = models.CharField(max_length=100, null=True, blank=True)
    skills = models.CharField(max_length=100, null=True, blank=True)
    specials = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return "Rang {} ({} - {})".format(self.ranking, self.min_rang, self.max_rang)

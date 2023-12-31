from datetime import date
import re, sys
from sentry_sdk import capture_message

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import Max, Sum
from django.shortcuts import get_object_or_404

from django_resized import ResizedImageField
from markdownfield.models import MarkdownField, RenderedMarkdownField
from markdownfield.validators import VALIDATOR_STANDARD

from log.create_log import logStufenaufstieg
from shop.models import *

from . import enums

def get_tier_cost_with_sp() -> dict:
    return {
        1: 1,
        2: 1,
        3: 1,
        4: 2,
        5: 2,
        6: 2,
        7: 3
    }

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

    skilled_gfs = models.ManyToManyField("Gfs", blank=True, related_name="skilled_gfs")

    def __str__(self):
        return self.titel


class Wesen(models.Model):

    class Meta:
        ordering = ['komplexität']
        verbose_name = "Wesen"
        verbose_name_plural = "Wesen"

    komplexität = models.PositiveIntegerField(default=0)

    icon = ResizedImageField(size=[64, 64], null=True, blank=True)
    titel = models.CharField(max_length=20, unique=True)
    beschreibung = MarkdownField(rendered_field='beschreibung_rendered', validator=VALIDATOR_STANDARD)
    beschreibung_rendered = RenderedMarkdownField(null=True)

    def __str__(self):
        return self.titel


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
        verbose_name = "Gfs/Klasse"
        verbose_name_plural = "Gfs/Klassen"

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
        unique_together = ["stufe"]

    stufe = models.PositiveIntegerField(default=0)
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

    bedingung = models.ManyToManyField("Talent", blank=True)

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

    titel = models.CharField(max_length=40)
    ip = models.PositiveIntegerField(default=0, validators=[MaxValueValidator(1000)])
    min_ip = models.PositiveIntegerField(default=0, validators=[MaxValueValidator(1000)])
    max_ip = models.PositiveIntegerField(default=0, validators=[MaxValueValidator(1000)])
    beschreibung = models.TextField(max_length=1000, blank=True, default="")

    wann_wählbar = models.CharField(max_length=1, choices=enums.teil_erstellung_enum, default=enums.teil_erstellung_enum[0][0])
    is_sellable = models.BooleanField(default=True, verbose_name="ist verkaufbar?")
    max_amount = models.PositiveSmallIntegerField(default=1, null=True, blank=True, help_text="Leer lassen für keine Beschränkung")

    needs_attribut = models.BooleanField(default=False)
    needs_fertigkeit = models.BooleanField(default=False)
    needs_engelsroboter = models.BooleanField(default=False)
    needs_notiz = models.BooleanField(default=False)
    needs_ip = models.BooleanField(default=False)

    needs_implementation = models.BooleanField(default=False, verbose_name="muss implementiert werden")
    has_implementation = models.BooleanField(default=False, verbose_name="ist implementiert")


class Vorteil(Teil):

    class Meta:
        ordering = ['titel', 'ip']
        verbose_name_plural = "Vorteile"
        verbose_name = "Vorteil"

        unique_together = (('titel', 'ip', "beschreibung"),)

    def __str__(self):
        return "{} (kostet {} IP)".format(self.titel, self.ip)


class Nachteil(Teil):

    class Meta:
        ordering = ['titel', 'ip']
        verbose_name_plural = "Nachteile"
        verbose_name = "Nachteil"

        unique_together = (('titel', 'ip', "beschreibung"),)

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
    beschreibung = models.CharField(max_length=100, blank=True, default='')
    
    attribut = models.ForeignKey(Attribut, null=True, on_delete=models.SET_NULL)
    gruppe = models.CharField(max_length=1, choices=enums.gruppen_enum, null=True)

    impro_possible = models.BooleanField(default=True)
    limit = models.CharField(choices=enums.limit_enum, max_length=20, default=enums.limit_enum[0])

    def __str__(self):
        return "{} ({})".format(self.titel, self.attribut)


class Wissensfertigkeit(models.Model):

    WISSENSF_STUFENFAKTOR = 3

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


class Charakter(models.Model):

    class Meta:
        verbose_name = "Charakter"
        verbose_name_plural = "Charaktere"
        ordering = ["eigentümer", 'name']

    image = ResizedImageField(size=[1024, 1024], null=True, blank=True)

    # settings
    in_erstellung = models.BooleanField(default=True)
    larp = models.BooleanField(default=False)
    eigentümer = models.ForeignKey(Spieler, on_delete=models.CASCADE, null=True, blank=True)
    gfs = models.ForeignKey(Gfs, on_delete=models.SET_NULL, null=True, blank=True)

    # manifest
    manifest = models.DecimalField('Startmanifest', max_digits=4, decimal_places=2, default=10.0,
                                   validators=[MaxValueValidator(10), MinValueValidator(0)])
    sonstiger_manifestverlust = models.DecimalField("sonstiger Manifestverlust", max_digits=4, decimal_places=2, default=0.0,
                                                    validators=[MaxValueValidator(10), MinValueValidator(0)])
    notizen_sonstiger_manifestverlust = models.CharField(max_length=200, default="", blank=True)

    # roleplay
    name = models.CharField(max_length=200, null=True)
    gewicht = models.FloatField(null=True, validators=[MinValueValidator(0)], verbose_name="Gewicht in kg")
    größe = models.PositiveIntegerField(null=True, verbose_name="Größe in cm")
    alter = models.PositiveIntegerField(null=True)
    geschlecht = models.CharField(max_length=100, null=True)
    sexualität = models.CharField(max_length=100, blank=True, null=True)
    beruf = models.ForeignKey(Beruf, on_delete=models.SET_NULL, null=True, blank=True)
    präf_arm = models.CharField(max_length=100, null=True, blank=True, verbose_name="präferierter Arm (rechts/links?)")
    religion = models.ForeignKey(Religion, on_delete=models.SET_NULL, null=True, blank=True)
    hautfarbe = models.CharField(max_length=100, default="")
    haarfarbe = models.CharField(max_length=100, default="")
    augenfarbe = models.CharField(max_length=100, default="")

    # currencies
    ap = models.PositiveIntegerField(null=True, blank=True)
    fp = models.PositiveIntegerField(null=True, blank=True)
    fg = models.PositiveIntegerField(null=True, blank=True)
    sp = models.PositiveIntegerField(null=True, blank=True)
    ip = models.IntegerField(null=True, blank=True)
    tp = models.PositiveSmallIntegerField(default=0)
    spF_wF = models.IntegerField(null=True, blank=True)
    wp = models.IntegerField(null=True, blank=True)
    zauberplätze = models.JSONField(default=dict, null=False, blank=True) # {"0": 2, "2": 1}
    geld = models.IntegerField(default=0)
    konzentration = models.PositiveSmallIntegerField(null=True, blank=True)
    prestige = models.PositiveIntegerField(default=0)
    verzehr = models.PositiveIntegerField(default=0)

    # Kampagne
    ep = models.PositiveIntegerField(default=0)
    ep_stufe = models.PositiveIntegerField(default=0, verbose_name="aktuelle Stufe des Charakters")
    ep_stufe_in_progress = models.PositiveIntegerField(default=0, verbose_name="Stufe des Charakters, die noch verteilt werden muss")
    skilltree_stufe = models.PositiveSmallIntegerField(default=1)
    processing_notes = models.JSONField(default=dict, null=False, blank=True)

    # HP
    HPplus_geistig = models.IntegerField(default=0)
    HPplus = models.IntegerField(default=0)
    HPplus_fix = models.IntegerField(default=None, null=True, blank=True)
    rang = models.PositiveIntegerField(default=0)
    larp_rang = models.PositiveIntegerField(default=0)

    # kampf
    wesenschaden_waff_kampf = models.IntegerField(default=0)
    wesenschaden_andere_gestalt = models.IntegerField("BS andere Gestalt", blank=True, null=True)
    crit_attack = models.PositiveSmallIntegerField(default=0)
    crit_defense = models.PositiveSmallIntegerField(default=0)
    initiative_bonus = models.SmallIntegerField(default=0)
    reaktion_bonus = models.SmallIntegerField(default=0)
    natürlicher_schadenswiderstand_bonus = models.SmallIntegerField(default=0)
    astralwiderstand_bonus = models.SmallIntegerField(default=0)
    manaoverflow_bonus = models.SmallIntegerField(default=0)

    # Geschreibsel
    notizen = models.TextField(blank=True, null=True)
    persönlicheZiele = models.TextField(blank=True, null=True)
    sonstige_items = models.TextField(default='', blank=True)
    sonstiges_alchemie = models.TextField(default='', blank=True)
    sonstiges_cyberware = models.TextField(default='', blank=True)

    # M2M #

    vorteile = models.ManyToManyField(Vorteil, through="character.RelVorteil", blank=True)
    nachteile = models.ManyToManyField(Nachteil, through="character.RelNachteil", blank=True)
    talente = models.ManyToManyField(Talent, through="character.RelTalent", blank=True)

    persönlichkeit = models.ManyToManyField(Persönlichkeit, blank=True)
    wesenkräfte = models.ManyToManyField(Wesenkraft, through="character.RelWesenkraft", blank=True)

    attribute = models.ManyToManyField(Attribut, through="character.RelAttribut", blank=True)
    fertigkeiten = models.ManyToManyField(Fertigkeit, through='character.RelFertigkeit', blank=True)
    spezialfertigkeiten = models.ManyToManyField(Spezialfertigkeit, through='character.RelSpezialfertigkeit', blank=True)
    wissensfertigkeiten = models.ManyToManyField(Wissensfertigkeit, through='character.RelWissensfertigkeit', blank=True)
    gfs_fähigkeiten = models.ManyToManyField(GfsAbility, through='character.RelGfsAbility', blank=True)

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

    def __str__(self):
        return "{} ({})".format(self.name, self.eigentümer)

    def get_konzentration(self):
        return self.konzentration if self.konzentration is not None else RelAttribut.objects.get(char=self, attribut__titel="IN").aktuell() * 5

    def get_max_stufe(self) -> int:
        return GfsStufenplanBase.objects.filter(ep__lte=self.ep).aggregate(Max("stufe"))["stufe__max"] or 0

    def max_tier_allowed(self) -> int:
        new_tiers_at_stufe = [0, 2, 5, 8, 12, 16, 20]
        return len([stufe for stufe in new_tiers_at_stufe if stufe <= self.ep_stufe_in_progress])

    def init_stufenhub(self):
        # new Stufe verteilen?
        max_stufe = self.get_max_stufe()
        if self.ep_stufe_in_progress >= max_stufe or self.gfs is None: return

        base_qs = self.gfs.gfsstufenplan_set\
            .prefetch_related("basis")\
            .filter(basis__stufe__gt=self.ep_stufe_in_progress or self.ep_stufe, basis__stufe__lte=max_stufe)


        # numeric values
        numeric_values = base_qs.aggregate(
            ap=Sum("basis__ap"),
            fp=Sum("basis__fp"),
            fg=Sum("basis__fg"),
            tp=Sum("basis__tp"),
        )
        
        # persist numeric values
        self.ap += numeric_values["ap"]
        self.fp += numeric_values["fp"]
        self.fg += numeric_values["fg"]
        self.tp += numeric_values["tp"]
        self.ep_stufe_in_progress = max_stufe

        self.save(update_fields=["ap", "fp", "fg", "tp", "ep_stufe_in_progress"])


        # gfs-abilities
        for st in base_qs.filter(ability__isnull=False):
            RelGfsAbility.objects.get_or_create(char=self, ability=st.ability)


        # vorteile
        vorteil_ids_new = base_qs.filter(vorteile__isnull=False).values_list("vorteile__id", flat=True)
        vorteil_ids_current = RelVorteil.objects.prefetch_related("teil").filter(char=self, teil__id__in=vorteil_ids_new).values_list("teil__id", flat=True)

        for vorteil_id in set(vorteil_ids_new):
            vorteil = Vorteil.objects.get(id=vorteil_id)

            # sum of all vorteile
            sum_current = len([teil_id for teil_id in vorteil_ids_current if teil_id == vorteil_id])
            sum_new = len([teil_id for teil_id in vorteil_ids_new if teil_id == vorteil_id])
            total_sum = sum_current + sum_new

            max_amount = vorteil.max_amount if vorteil.max_amount is not None else sys.maxsize
            amount_in_overflow = total_sum - max_amount

            # some not allowed, give ip
            if amount_in_overflow > 0:
                if not hasattr(self.processing_notes, "campaign") or not self.processing_notes["campaign"]:
                    self.processing_notes["campaign"] = []

                self.processing_notes["campaign"].append(f"Du erhälst je {vorteil.ip} IP für {amount_in_overflow}x {vorteil.titel}")
                self.ip += amount_in_overflow * vorteil.ip

            # add new RelVorteil, (also the ones that need more information, see "will_create=True")
            amount_to_create = min(max_amount - sum_current, sum_new)
            if amount_to_create > 0:
                for _ in range(amount_to_create):
                    rel = RelVorteil.objects.create(teil=vorteil, char=self)
                    rel.update_will_create()
        
        self.save(update_fields=["ip", "processing_notes"])


        # zauber
        if not hasattr(self, "zauberplätze") or not self.zauberplätze: self.zauberplätze = {}
        for plan in base_qs.filter(zauber__gt=0):
            stufe = plan.basis.stufe
            current = self.zauberplätze[stufe] if hasattr(self.zauberplätze, f"{stufe}") else 0
            self.zauberplätze[stufe] = current + plan.zauber

        self.save(update_fields=["zauberplätze"])


        # wesenkräfte
        wesenkräfte = []
        for stufe in base_qs:
            for wk in stufe.wesenkräfte.all():
                wesenkräfte.append(wk)

        for w in wesenkräfte:
            _, created = RelWesenkraft.objects.get_or_create(char=self, wesenkraft=w, defaults={"tier": 1 if w.skilled_gfs.filter(id=self.gfs.id).exists() else 0})
            if not created:
                # log that wesenkraft already existed
                capture_message(f"Wesenkraft {w.titel} war bei {self.name} ({self.gfs.titel}) im EP-Tree Stufe {self.ep_stufe+1} - {self.ep_stufe_in_progress}", level='info')

        logStufenaufstieg(self.eigentümer, self)


    def submit_stufenhub(self):
        from levelUp.decorators import is_done_entirely
        if self.gfs is None or not is_done_entirely(self): return

        if hasattr(self.processing_notes, "campaign"):
            del self.processing_notes["campaign"]

        # attributes
        rels = []
        for rel in RelAttribut.objects.filter(char=self):
            rel.aktuellerWert += rel.aktuellerWert_temp
            rel.aktuellerWert_temp = 0

            rel.maxWert += rel.maxWert_temp
            rel.maxWert_temp = 0

            rels.append(rel)
        RelAttribut.objects.bulk_update(rels, ["aktuellerWert", "aktuellerWert_temp", "maxWert", "maxWert_temp"])

        # gruppen
        rels = []
        for rel in RelGruppe.objects.filter(char=self):
            rel.fg += rel.fg_temp
            rel.fg_temp = 0

            rels.append(rel)
        RelGruppe.objects.bulk_update(rels, ["fg", "fg_temp"])

        # fertigkeiten
        rels = []
        for rel in RelFertigkeit.objects.filter(char=self):
            rel.fp += rel.fp_temp
            rel.fp_temp = 0
            rels.append(rel)
        RelFertigkeit.objects.bulk_update(rels, ["fp", "fp_temp"])

        # ep-stufe
        self.in_erstellung = False
        self.ep_stufe = self.ep_stufe_in_progress
        self.save(update_fields=["ep_stufe", "processing_notes", "in_erstellung"])


class RelWesenkraft(models.Model):

    class Meta:
        ordering = ['char', 'wesenkraft']
        verbose_name = "Wesenkraft"
        verbose_name_plural = "Wesenkräfte"

        unique_together = (('char', 'wesenkraft'),)

    char = models.ForeignKey(Charakter, on_delete=models.CASCADE)
    wesenkraft = models.ForeignKey(Wesenkraft, on_delete=models.CASCADE)

    tier = models.PositiveSmallIntegerField(default=0, validators=[MaxValueValidator(7)])

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
        unique_together = ["teil", "char", "notizen"]

    char = models.ForeignKey(Charakter, on_delete=models.CASCADE)
    teil = None

    notizen = models.CharField(max_length=500, blank=True, null=True)

    attribut = models.ForeignKey(Attribut, on_delete=models.SET_NULL, null=True, blank=True)
    fertigkeit = models.ForeignKey(Fertigkeit, on_delete=models.SET_NULL, null=True, blank=True)
    engelsroboter = models.ForeignKey(Engelsroboter, on_delete=models.SET_NULL, null=True, blank=True)
    ip = models.PositiveSmallIntegerField(null=True, blank=True)

    will_create = models.BooleanField(default=False)
    is_sellable = models.BooleanField(default=True, verbose_name="ist verkaufbar?")

    def __str__(self):
        return "'{}' zu Charakter '{}'".format(self.teil.titel, self.char.name)
    
    def update_will_create(self):
        will_create = (self.teil.needs_attribut and not self.attribut) or\
            (self.teil.needs_fertigkeit and not self.fertigkeit) or\
            (self.teil.needs_engelsroboter and not self.engelsroboter) or\
            (self.teil.needs_notiz and not self.notizen)

        if self.will_create != will_create:
            self.will_create = will_create
            self.save(update_fields=["will_create"])

    def full_addons(self):
        addons = []
        if self.teil.needs_ip: addons.append(f"{self.ip} IP")
        if self.teil.needs_attribut and self.attribut: addons.append(self.attribut.titel)
        if self.teil.needs_fertigkeit and self.fertigkeit: addons.append(self.fertigkeit.titel)
        if self.teil.needs_engelsroboter and self.engelsroboter: addons.append(self.engelsroboter.name)
        if self.notizen: addons.append(self.notizen)

        return ', '.join(addons) if len(addons) else ""

    def __repr__(self):
        if self.will_create: return self.teil.titel + "(WILL CREATE)"

        addons = self.full_addons()
        return self.teil.titel + (f" ({addons})" if len(addons) else "")


class RelVorteil(RelTeil):
    class Meta:
        verbose_name = "Vorteil"
        verbose_name_plural = "Vorteile"

    teil = models.ForeignKey(Vorteil, on_delete=models.CASCADE)


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
    maxWert_fix = models.PositiveIntegerField(null=True, blank=True)

    def __str__(self):
        return "'{}' von '{}'".format(self.attribut.__str__(), self.char.__str__())

    def aktuell(self): return self.aktuellerWert + self.aktuellerWert_temp + self.aktuellerWert_bonus
    def max(self): return self.maxWert + self.maxWert_temp

class RelGruppe(models.Model):
    
    class Meta:
        ordering = ['char', 'gruppe']
        verbose_name = "Fertigkeitsgruppe"
        verbose_name_plural = "Fertigkeitsgruppen"

        unique_together = (('char', 'gruppe'),)

    char = models.ForeignKey(Charakter, on_delete=models.CASCADE)
    gruppe = models.CharField(max_length=1, choices=enums.gruppen_enum)

    fg = models.SmallIntegerField(default=0)
    fg_temp = models.SmallIntegerField(default=0)

    def __str__(self):
        return "'{}' von '{}'".format(self.get_gruppe_display(), self.char.__str__())


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


class RelWissensfertigkeit(models.Model):

    class Meta:
        ordering = ['char', 'wissensfertigkeit']
        verbose_name = "Wissensfertigkeit"
        verbose_name_plural = "Wissensfertigkeiten"

        unique_together = (('char', 'wissensfertigkeit'),)

    char = models.ForeignKey(Charakter, on_delete=models.CASCADE)
    wissensfertigkeit = models.ForeignKey(Wissensfertigkeit, on_delete=models.CASCADE)

    stufe = models.PositiveSmallIntegerField(default=0, null=False, blank=False, validators=[MaxValueValidator(15)])

    def __str__(self):
        return "'{}' von '{}'".format(self.wissensfertigkeit.__str__(), self.char.__str__())


class RelSpezialfertigkeit(models.Model):
    class Meta:
        ordering = ['char', 'spezialfertigkeit']
        verbose_name = "Spezialfertigkeit"
        verbose_name_plural = "Spezialfertigkeiten"

        unique_together = (('char', 'spezialfertigkeit'),)

    char = models.ForeignKey(Charakter, on_delete=models.CASCADE)
    spezialfertigkeit = models.ForeignKey(Spezialfertigkeit, on_delete=models.CASCADE)

    stufe = models.PositiveIntegerField(default=0, validators=[MaxValueValidator(15)])

    def __str__(self):
        return "'{}' von '{}'".format(self.spezialfertigkeit.__str__(), self.char.__str__())


class RelGfsAbility(models.Model):
    class Meta:
        ordering = ['char', 'ability']
        verbose_name = "Gfs-Fähigkeit"
        verbose_name_plural = "Gfs-Fähigkeiten"

        unique_together = (('char', 'ability'),)

    char = models.ForeignKey(Charakter, on_delete=models.CASCADE)
    ability = models.ForeignKey(GfsAbility, on_delete=models.CASCADE)

    notizen = models.TextField(null=True, blank=True)

    def __str__(self):
        return "'{}' von '{}'".format(self.ability.__str__(), self.char.__str__())


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
    tier = models.PositiveSmallIntegerField(default=0, validators=[MaxValueValidator(7)])

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
        verbose_name = "Base Skilltree"
        verbose_name_plural = "Base Skilltrees"

        ordering = ["stufe"]

    # stufe == 0: Bonus
    stufe = models.PositiveIntegerField(validators=[MaxValueValidator(10)], default=1, unique=True)
    sp = models.PositiveIntegerField(default=1)

    def __str__(self):
        return "Skilltree-Base Stufe {} ({} SP)".format(self.stufe, self.sp)


class GfsSkilltreeEntry(models.Model):
    class Meta:
        verbose_name = "Gfs Skilltree"
        verbose_name_plural = "Gfs Skilltrees"

        ordering = ["gfs", "base", "operation"]

    base = models.ForeignKey(SkilltreeBase, on_delete=models.CASCADE)
    gfs = models.ForeignKey(Gfs, on_delete=models.CASCADE)

    operation = models.CharField(max_length=1, choices=enums.skilltreeentry_enum, default="R", null=False, blank=False, help_text="wichtigstes Feld, bestimmt die Art des Eintrags und welche anderen Felder benötigt werden.")

    amount = models.SmallIntegerField(null=True, blank=True, help_text="für AP, FP, FG, SP, IP, TP und Anz. Zauber-slots, WP in Speizis/Wissis, Fertigkeitsboni, Crit und HP")
    stufe = models.SmallIntegerField(null=True, blank=True, help_text="für Zauber-slots und Stufen von Items")
    text = models.TextField(null=True, blank=True, help_text="für Vor-/Nachteilnotizen und alles nicht-implementierbare, z. B. Bonuseffekte bei Angriffen")

    fertigkeit = models.ForeignKey(Fertigkeit, on_delete=models.SET_NULL, null=True, blank=True, help_text="für Bonus in Fertigkeit und  ggf. Vor-/Nachteile wie Spezialisiert, die eine Fertigkeit brauchen.")
    vorteil = models.ForeignKey(Vorteil, on_delete=models.SET_NULL, null=True, blank=True, help_text="für neuen Vorteil")
    nachteil = models.ForeignKey(Nachteil, on_delete=models.SET_NULL, null=True, blank=True, help_text="für neuen Nachteil")
    
    wesenkraft = models.ForeignKey(Wesenkraft, on_delete=models.SET_NULL, null=True, blank=True, help_text="Für neue Wesenkraft")
    spezialfertigkeit = models.ForeignKey(Spezialfertigkeit, on_delete=models.SET_NULL, null=True, blank=True, help_text="Für neue Spezi oder WP in einer Spezi")
    wissensfertigkeit = models.ForeignKey(Wissensfertigkeit, on_delete=models.SET_NULL, null=True, blank=True, help_text="Für neue Wissi oder WP in einer Wissi")

    # shop
    magische_ausrüstung = models.ForeignKey(Magische_Ausrüstung, on_delete=models.SET_NULL, null=True, blank=True, help_text="Für ein magisches Item")

    def __str__(self):
        return f"{self.gfs} Stufe {self.base.stufe}: {self.get_operation_display()}"
    
    def __repr__(self) -> str:
        try:

            # AP, FP, FG, SP, IP, TP, Crit-Angriff, Crit-Verteidigung, körperliche HP, geistige HP, HP Schaden waff. Kampf,
            # Initiative fix, Reaktion, natürlicher Schadenswiderstand, Astral-Widerstand
            if self.operation in ["a", "f", "F", "p", "i", "t", "A", "V", "K", "G", "k", "I", "r", "N", "T"]:
                return f"+{self.amount} {self.get_operation_display()}"

            # Roleplay-Text
            if self.operation == "R": return f"{self.text} (Achtung, keine automatische Verechnung!)"
            
            # optional Stufe: Zauberslots, magisches Item
            if self.operation == "z": return f"{self.amount} Zauberslots" + (f" Stufe {self.stufe}" if self.stufe else "")
            if self.operation == "h": return f"{self.amount} {self.magische_ausrüstung.name}" + (f" Stufe {self.stufe}" if self.stufe else "")

            # Bonus in Fertigkeit
            if self.operation == "B": return f"+{self.amount} Bonus in {self.fertigkeit.titel}"

            # neu! (Wesenkraft, Spezi, Wissi)
            if self.operation == "e": return self.wesenkraft.titel
            if self.operation == "s": return self.spezialfertigkeit.titel
            if self.operation == "w": return self.wissensfertigkeit.titel

            # WP in Spezialfertigkeit & Wissensfertigkeit
            if self.operation == "S": return f"+{self.amount} WP in {self.spezialfertigkeit.titel}"
            if self.operation == "W": return f"+{self.amount} WP in {self.wissensfertigkeit.titel}"

            # new Teil
            if self.operation == "v": return f"{self.vorteil.titel}" + (f" {self.text}" if self.text else "") + (f" ({self.fertigkeit.titel})" if self.fertigkeit else "")
            if self.operation == "n": return f"{self.nachteil.titel}" + (f" {self.text}" if self.text else "") + (f" ({self.fertigkeit.titel})" if self.fertigkeit else "")
    
        except:
            return f"FORMAT ERROR bei {self.get_operation_display()}"

    def apply_to(self, char: Charakter) -> None:

        # AP
        if self.operation == "a":
            char.ap += self.amount
            char.save(update_fields=["ap"])
            return
        # FP
        if self.operation == "f":
            char.fp += self.amount
            char.save(update_fields=["fp"])
            return
        # FG
        if self.operation == "F":
            char.fg += self.amount
            char.save(update_fields=["fg"])
            return
        # SP
        if self.operation == "s":
            char.sp += self.amount
            char.save(update_fields=["sp"])
            return
        # IP
        if self.operation == "i":
            char.ip += self.amount
            char.save(update_fields=["ip"])
            return
        # TP
        if self.operation == "t":
            char.tp += self.amount
            char.save(update_fields=["tp"])
            return
        # Crit-Angriff
        if self.operation == "A":
            char.crit_attack += self.amount
            char.save(update_fields=["crit_attack"])
            return
        # Crit-Verteidigung
        if self.operation == "V":
            char.crit_defense += self.amount
            char.save(update_fields=["crit_defense"])
            return
        # körperliche HP
        if self.operation == "K":
            char.HPplus += self.amount
            char.save(update_fields=["HPplus"])
            return
        # geistige HP
        if self.operation == "G":
            char.HPplus_geistig += self.amount
            char.save(update_fields=["HPplus_geistig"])
            return
        # HP Schaden waff. Kampf
        if self.operation == "k":
            if not char.wesenschaden_waff_kampf: char.wesenschaden_waff_kampf = 0
            if not char.wesenschaden_andere_gestalt: char.wesenschaden_andere_gestalt = 0
            char.wesenschaden_waff_kampf += self.amount
            char.wesenschaden_andere_gestalt += self.amount
            char.save(update_fields=["wesenschaden_waff_kampf", "wesenschaden_andere_gestalt"])
            return
        # Initiative fix
        if self.operation == "I":
            char.initiative_bonus += self.amount
            char.save(update_fields=["initiative_bonus"])
            return
        # Reaktion
        if self.operation == "r":
            char.reaktion_bonus += self.amount
            char.save(update_fields=["areaktion_bonusp"])
            return
        # natürlicher Schadenswiderstand
        if self.operation == "N":
            char.natürlicher_schadenswiderstand_bonus += self.amount
            char.save(update_fields=["natürlicher_schadenswiderstand_bonus"])
            return
        # Astral-Widerstand
        if self.operation == "T":
            char.astralwiderstand_bonus += self.amount
            char.save(update_fields=["astralwiderstand_bonus"])
            return

        # Roleplay-Text
        if self.operation == "R":
            if not char.processing_notes: char.processing_notes = {}
            if "skilltree" not in char.processing_notes: char.processing_notes["skilltree"] = []
            char.processing_notes["skilltree"].append(f"{self.__repr__()} (Skilltree St. {self.base.stufe})")
            char.save(update_fields=["processing_notes"])
            return
        
        # Zauberslots
        if self.operation == "z":
            stufe = self.stufe if self.stufe is not None else 30
            prev_amount = char.zauberplätze[str(stufe)] if stufe in char.zauberplätze else 0
            char.zauberplätze[str(stufe)] = prev_amount + self.amount
            char.save(update_fields=["zauberplätze"])
            return

        # magisches Item
        if self.operation == "h":
            rel, created = RelMagische_Ausrüstung.objects.get_or_create(item=self.magische_ausrüstung, char=char, stufe=self.stufe)
            rel.amount += self.amount
            rel.save(update_fields=["amount"])
            return

        # Bonus in Fertigkeit
        if self.operation == "B":
            relfert = RelFertigkeit.objects.get(char=char, fertigkeit=self.fertigkeit)
            relfert.fp_bonus += self.amount
            char.save(update_fields=["sp"])
            relfert.save(update_fields=["fp_bonus"])
            return

        # neu! Wesenkraft
        if self.operation == "e":
            RelWesenkraft.objects.get_or_create(char=char, wesenkraft=self.wesenkraft, defaults={"tier": 1 if self.wesenkraft.skilled_gfs.filter(id=self.gfs).exists() else 0})
            return
        # neu! Spezi
        if self.operation == "s":
            RelSpezialfertigkeit.objects.get_or_create(char=char, spezialfertigkeit=self.spezialfertigkeit)
            return
        # neu! Wissi
        if self.operation == "w":
            RelWissensfertigkeit.objects.get_or_create(char=char, wissensfertigkeit=self.wissensfertigkeit)
            return

        # new Vorteil
        if self.operation == "v":
            RelVorteil.objects.create(char=char, teil=self.vorteil, fertigkeit=self.fertigkeit, notizen=self.text if self.text else None, is_sellable=self.vorteil.is_sellable)
            return
        # new Nachteil
        if self.operation == "n":
            RelVorteil.objects.create(char=char, teil=self.nachteil, fertigkeit=self.fertigkeit, notizen=self.text if self.text else None, is_sellable=self.nachteil.is_sellable)
            return
        
        # WP in Spezialfertigkeit
        created = False
        if self.operation == "S":
            rel, created = RelSpezialfertigkeit.objects.get_or_create(char=char, spezialfertigkeit=self.spezialfertigkeit)
            rel.stufe += self.amount
            rel.save(update_fields=["stufe"])
        # WP in Wissensfertigkeit
        if self.operation == "W":
            rel, created = RelWissensfertigkeit.objects.get_or_create(char=char, wissensfertigkeit=self.wissensfertigkeit)
            rel.stufe += self.amount
            rel.save(update_fields=["stufe"])

        # pay for new spezi/wissi where possible
        if created and char.sp > 0:
            char.sp -= 1
            char.save(update_fields=["sp"])

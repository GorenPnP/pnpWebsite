import enum, sys, math
from datetime import date
from sentry_sdk import capture_message

from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import Max, Sum, Subquery, OuterRef, F, Q, Exists, Value
from django.db.models.functions import Coalesce
from django.db.models.query import QuerySet
from django.utils.translation import gettext as _

from django_resized import ResizedImageField
from markdownfield.models import MarkdownField, RenderedMarkdownField
from markdownfield.validators import VALIDATOR_STANDARD

from log.create_log import logStufenaufstieg
from shop.models import *

from .. import enums
from ..permissions import CustomPermission
from .base import *
from .gfs import *
from .rel import *


class Charakter(models.Model):

    class Meta:
        verbose_name = "Charakter"
        verbose_name_plural = "Charaktere"
        ordering = ["eigentümer", 'name']

    image = ResizedImageField(size=[1024, 1024], null=True, blank=True, verbose_name="Bild")

    # settings
    in_erstellung = models.BooleanField(default=True)
    reduced_rewards_until_klasse_stufe = models.PositiveSmallIntegerField(default=0)
    no_MA = models.BooleanField(default=False, verbose_name="Managetik können, aber für immer auf Magie verzichten")
    no_MA_MG = models.BooleanField(default=False, verbose_name="Für immer auf Magie und Managetik verzichten")
    larp = models.BooleanField(default=False)
    eigentümer = models.ForeignKey(Spieler, on_delete=models.CASCADE, null=True, blank=True)
    gfs = models.ForeignKey(Gfs, on_delete=models.SET_NULL, null=True, blank=True)
    persönlichkeit = models.ForeignKey(Persönlichkeit, on_delete=models.SET_NULL, null=True, blank=True)

    # manifest
    manifest = models.DecimalField('Startmanifest', max_digits=4, decimal_places=2, default=10.0,
                                   validators=[MaxValueValidator(10), MinValueValidator(0)])
    sonstiger_manifestverlust = models.DecimalField("sonstiger Manifestverlust", max_digits=4, decimal_places=2, default=0.0,
                                                    validators=[MaxValueValidator(10), MinValueValidator(0)])
    notizen_sonstiger_manifestverlust = models.TextField(default="", blank=True)
    manifest_fix = models.DecimalField(max_digits=4, decimal_places=2, default=None, null=True, blank=True)

    # roleplay
    name = models.CharField(max_length=200, null=True, blank=True)
    gewicht = models.FloatField(null=True, blank=True, validators=[MinValueValidator(0)], verbose_name="Gewicht in kg")
    größe = models.PositiveIntegerField(null=True, blank=True, verbose_name="Größe in cm")
    alter = models.PositiveIntegerField(null=True, blank=True)
    geschlecht = models.CharField(max_length=100, null=True, blank=True)
    sexualität = models.CharField(max_length=100, blank=True, null=True)
    beruf = models.ForeignKey(Beruf, on_delete=models.SET_NULL, null=True, blank=True)
    präf_arm = models.CharField(max_length=100, null=True, blank=True, verbose_name="präferierter Arm (rechts/links?)")
    religion = models.ForeignKey(Religion, on_delete=models.SET_NULL, null=True, blank=True)
    hautfarbe = models.CharField(max_length=100, default="", blank=True)
    haarfarbe = models.CharField(max_length=100, default="", blank=True)
    augenfarbe = models.CharField(max_length=100, default="", blank=True)

    # currencies
    ap = models.PositiveIntegerField(null=True, blank=True)
    fp = models.PositiveIntegerField(null=True, blank=True)
    fg = models.PositiveIntegerField(null=True, blank=True)
    sp = models.PositiveIntegerField(null=True, blank=True)
    sp_fix = models.PositiveIntegerField(default=None, null=True, blank=True)
    ip = models.IntegerField(null=True, blank=True)
    tp = models.PositiveSmallIntegerField(default=0)
    spF_wF = models.IntegerField(null=True, blank=True)
    wp = models.IntegerField(null=True, blank=True)
    zauberplätze = models.JSONField(default=dict, null=False, blank=True) # {"0": 2, "2": 1}
    konzentration = models.PositiveSmallIntegerField(null=True, blank=True)
    konzentration_fix = models.SmallIntegerField(default=None, null=True, blank=True)
    prestige = models.PositiveIntegerField(default=0)
    verzehr = models.PositiveIntegerField(default=0)
    glück = models.PositiveIntegerField(default=100)
    sanität = models.PositiveIntegerField(default=100)

    # Kampagne
    ep = models.PositiveIntegerField(default=0)
    ep_stufe = models.PositiveIntegerField(default=1, verbose_name="aktuelle Stufe des Charakters")
    ep_stufe_in_progress = models.PositiveIntegerField(default=1, verbose_name="Stufe des Charakters, die noch verteilt werden muss")
    skilltree_stufe = models.PositiveSmallIntegerField(default=1)
    processing_notes = models.JSONField(default=dict, null=False, blank=True)

    # HP
    HPplus_geistig = models.IntegerField(default=0)
    HPplus = models.IntegerField(default=0)
    HPplus_fix = models.IntegerField(default=None, null=True, blank=True)
    larp_rang = models.PositiveIntegerField(default=0)

    # kampf
    wesenschaden_waff_kampf = models.IntegerField(default=0)
    wesenschaden_andere_gestalt = models.IntegerField("BS andere Gestalt", blank=True, null=True)
    crit_attack = models.PositiveSmallIntegerField(default=0)
    crit_defense = models.PositiveSmallIntegerField(default=0)
    initiative_bonus = models.SmallIntegerField(default=0)
    physische_reaktion_bonus = models.SmallIntegerField(default=0)
    physischer_widerstand_bonus = models.SmallIntegerField(default=0)
    physischer_widerstand_bonus_str = models.CharField(max_length=128, default="", null=False, blank=True)
    astrale_reaktion_bonus = models.SmallIntegerField(default=0)
    astraler_widerstand_bonus_str = models.CharField(max_length=128, default="", null=False, blank=True)
    manaoverflow_bonus = models.SmallIntegerField(default=0)
    nat_regeneration_bonus = models.SmallIntegerField(default=0)
    immunsystem_bonus = models.SmallIntegerField(default=0)

    # movement speed
    speed_laufen_bonus = models.FloatField(default=0)
    speed_schwimmen_bonus = models.FloatField(default=0)
    speed_fliegen_bonus = models.FloatField(default=0)
    speed_astral_bonus = models.FloatField(default=0)

    # Geschreibsel
    notizen = models.TextField(blank=True, null=True)
    persönlicheZiele = models.TextField(blank=True, null=True)
    sonstige_items = models.TextField(default='', blank=True)

    # M2M #
    klassen = models.ManyToManyField(Klasse, through="character.RelKlasse", blank=True)
    vorteile = models.ManyToManyField(Vorteil, through="character.RelVorteil", blank=True)
    nachteile = models.ManyToManyField(Nachteil, through="character.RelNachteil", blank=True)
    talente = models.ManyToManyField(Talent, through="character.RelTalent", blank=True)
    wesenkräfte = models.ManyToManyField(Wesenkraft, through="character.RelWesenkraft", blank=True)

    attribute = models.ManyToManyField(Attribut, through="character.RelAttribut", blank=True)
    fertigkeiten = models.ManyToManyField(Fertigkeit, through='character.RelFertigkeit', blank=True)
    gruppen = models.ManyToManyField("RelGruppe", blank=True)
    spezialfertigkeiten = models.ManyToManyField(Spezialfertigkeit, through='character.RelSpezialfertigkeit', blank=True)
    wissensfertigkeiten = models.ManyToManyField(Wissensfertigkeit, through='character.RelWissensfertigkeit', blank=True)
    gfs_fähigkeiten = models.ManyToManyField(GfsAbility, through='character.RelGfsAbility', blank=True)
    klassen_fähigkeiten = models.ManyToManyField(KlasseAbility, through='character.RelKlasseAbility', blank=True)

    items = models.ManyToManyField(Item, through='character.RelItem', blank=True)
    nahkampfwaffen = models.ManyToManyField(Nahkampfwaffe, through='character.RelNahkampfwaffe', blank=True)
    munition = models.ManyToManyField(Munition, through='character.RelMunition', blank=True)
    fernkampfwaffen = models.ManyToManyField(Fernkampfwaffe, through='character.RelFernkampfwaffe', blank=True)
    magischeAusrüstung = models.ManyToManyField(Magische_Ausrüstung, through='character.RelMagische_Ausrüstung', blank=True)
    rituale_runen = models.ManyToManyField(Ritual_Rune, through='character.RelRitual_Rune', blank=True)
    rüstungen = models.ManyToManyField(Rüstung, through='character.RelRüstung', blank=True)
    technik = models.ManyToManyField(Technik, through='character.RelTechnik', blank=True)
    fahrzeuge = models.ManyToManyField(Fahrzeug, through='character.RelFahrzeug', blank=True)
    einbauten = models.ManyToManyField(Einbaute, through='character.RelEinbaute', blank=True)
    zauber = models.ManyToManyField(Zauber, through='character.RelZauber', blank=True)
    begleiter = models.ManyToManyField(Begleiter, through='character.RelBegleiter', blank=True)
    engelsroboter = models.ManyToManyField(Engelsroboter, through='character.RelEngelsroboter', blank=True)

    affektivitäten = models.ManyToManyField("Affektivität", blank=True)
    tags = models.ManyToManyField(Tag, blank=True)

    @property
    def geld(self):
        return self.card.money if self.card else None

    def __str__(self):
        return "{} ({})".format(self.name, self.eigentümer)

    def get_max_stufe(self) -> int:
        return GfsStufenplanBase.objects.filter(ep__lte=self.ep).aggregate(Max("stufe"))["stufe__max"] or 1

    def max_tier_allowed(self) -> int:
        new_tiers_at_stufe = [1, 2, 5, 8, 12, 16, 20]

        if self.larp: return len(new_tiers_at_stufe)
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
            _, created = RelWesenkraft.objects.get_or_create(char=self, wesenkraft=w, defaults={"tier": 0})
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


class Tag(models.Model):

    class Meta:
        verbose_name = "Tag"
        verbose_name_plural = "Tags"
        ordering = ["spieler", 'name']
        unique_together = ["spieler", 'name']

    spieler = models.ForeignKey(Spieler, on_delete=models.CASCADE)
    name = models.CharField(max_length=128, null=False, blank=False)

    def __str__(self):
        return self.name


class CurrentStory(models.Model):
    class Meta:
        ordering = ['char']

    char = models.OneToOneField(Charakter, on_delete=models.CASCADE)

    titel = models.TextField(null=True, blank=True)
    notes = models.TextField(null=True, blank=True, verbose_name="Notizen")
    
    mana = models.SmallIntegerField(null=True, blank=True)
    konz = models.SmallIntegerField(null=True, blank=True, verbose_name="Konzentration")
    gHP = models.SmallIntegerField(null=True, blank=True, verbose_name="geistige HP")
    kHP = models.SmallIntegerField(null=True, blank=True, verbose_name="körperliche HP")

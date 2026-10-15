from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import Sum, Subquery, OuterRef
from django.db.models.query import QuerySet

from shop.models import Engelsroboter

from .base import *
from .gfs import GfsAbility
from .klasse import Klasse, KlasseAbility, KlasseStufenplan


class RelWesenkraft(models.Model):

    class Meta:
        ordering = ['char', 'wesenkraft']
        verbose_name = "Wesenkraft"
        verbose_name_plural = "Wesenkräfte"

        unique_together = (('char', 'wesenkraft'),)

    char = models.ForeignKey("character.Charakter", on_delete=models.CASCADE)
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

    char = models.ForeignKey("character.Charakter", on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    wert = models.IntegerField(default=0, validators=[MinValueValidator(-200), MaxValueValidator(200)])
    notizen = models.CharField(max_length=100, blank=True, default='')

    def __str__(self):
        return "'{}' zu Charakter '{}'".format(self.name, self.char)


class RelTalent(models.Model):
    class Meta:
        ordering = ['char', 'talent']
        verbose_name = "Talent"
        verbose_name_plural = "Talente"

        unique_together = (('char', 'talent'),)

    char = models.ForeignKey("character.Charakter", on_delete=models.CASCADE)
    talent = models.ForeignKey(Talent, on_delete=models.CASCADE)

    def __str__(self):
        return "{} von {}".format(self.talent.titel, self.char.name)


class RelTeil(models.Model):
    """super for RelVorteil, RelNachteil"""
    class Meta:
        abstract = True
        ordering = ['char', 'teil']
        unique_together = ["teil", "char", "notizen"]

    char = models.ForeignKey("character.Charakter", on_delete=models.CASCADE)
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

        return ', '.join(addons) if addons else ""

    def __repr__(self):
        if self.will_create: return self.teil.titel + "(WILL CREATE)"

        addons = self.full_addons()
        return self.teil.titel + (f" ({addons})" if addons else "")


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

    char = models.ForeignKey("character.Charakter", on_delete=models.CASCADE)
    attribut = models.ForeignKey(Attribut, on_delete=models.CASCADE)

    aktuellerWert = models.PositiveIntegerField(default=0)
    aktuellerWert_temp = models.PositiveIntegerField(default=0)
    aktuellerWert_bonus = models.PositiveIntegerField(default=0)
    aktuellerWert_fix = models.PositiveIntegerField(null=True, blank=True)

    maxWert = models.PositiveIntegerField(default=0)
    maxWert_temp = models.PositiveIntegerField(default=0)
    maxWert_fix = models.PositiveIntegerField(null=True, blank=True)

    def __str__(self):
        if self.attribut.titel == "MA" and self.char.no_MA and not self.char.no_MA_MG:
            return f"'MG' von {self.char}"
        return f"'{self.attribut}' von '{self.char}'"

    def aktuell(self) -> int: return self.aktuellerWert + self.aktuellerWert_temp + self.aktuellerWert_bonus if self.aktuellerWert_fix is None else self.aktuellerWert_fix
    def max(self) -> int: return self.maxWert + self.maxWert_temp if self.maxWert_fix is None else self.maxWert_fix

class RelGruppe(models.Model):
    
    class Meta:
        ordering = ['char', 'gruppe']
        verbose_name = "Fertigkeitsgruppe"
        verbose_name_plural = "Fertigkeitsgruppen"

        unique_together = (('char', 'gruppe'),)

    char = models.ForeignKey("character.Charakter", on_delete=models.CASCADE)
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

    char = models.ForeignKey("character.Charakter", on_delete=models.CASCADE)
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

    char = models.ForeignKey("character.Charakter", on_delete=models.CASCADE)
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

    char = models.ForeignKey("character.Charakter", on_delete=models.CASCADE)
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

    char = models.ForeignKey("character.Charakter", on_delete=models.CASCADE)
    ability = models.ForeignKey(GfsAbility, on_delete=models.CASCADE)

    notizen = models.TextField(null=True, blank=True)

    def __str__(self):
        return "'{}' von '{}'".format(self.ability.__str__(), self.char.__str__())

class RelKlasseAbility(models.Model):
    class Meta:
        ordering = ['char', 'ability']
        verbose_name = "Klassen-Fähigkeit"
        verbose_name_plural = "Klassen-Fähigkeiten"

        unique_together = (('char', 'ability'),)

    char = models.ForeignKey("character.Charakter", on_delete=models.CASCADE)
    ability = models.ForeignKey(KlasseAbility, on_delete=models.CASCADE)

    notizen = models.TextField(null=True, blank=True)

    def __str__(self):
        return "'{}' von '{}'".format(self.ability.__str__(), self.char.name)


class RelKlasse(models.Model):
    class Meta:
        ordering = ['char', 'klasse']
        verbose_name = "Klasse"
        verbose_name_plural = "Klassen"

        unique_together = (('char', 'klasse'),)

    char = models.ForeignKey("character.Charakter", on_delete=models.CASCADE)
    klasse = models.ForeignKey(Klasse, on_delete=models.CASCADE)

    stufe = models.PositiveSmallIntegerField(default=1)

    def __str__(self):
        return "'{}' von '{}'".format(self.klasse.__str__(), self.char.__str__())

    @staticmethod
    def get_own_number_annotated(char: "Charakter") -> QuerySet["RelKlasse"]:
        get_SumSubquery = lambda field: KlasseStufenplan.objects\
            .filter(klasse=OuterRef("klasse"), stufe__lte=OuterRef("stufe"))\
            .values("klasse")\
            .annotate(sum=Sum(field))\
            .values("sum")

        return char.relklasse_set\
            .prefetch_related("klasse__base_abilities")\
            .annotate(
                ap = Subquery(get_SumSubquery("ap")),
                fp = Subquery(get_SumSubquery("fp")),
                fg = Subquery(get_SumSubquery("fg")),
                tp = Subquery(get_SumSubquery("tp")),
                ip = Subquery(get_SumSubquery("ip")),
                zauber = Subquery(get_SumSubquery("zauber")),
            )

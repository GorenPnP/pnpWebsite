from django.db import models
from django.shortcuts import get_object_or_404

from character.models import Gfs

class NewCharakter(models.Model):
    eigentümer = models.ForeignKey("character.Spieler", on_delete=models.CASCADE, null=True)
    ep_system = models.BooleanField(default=True)
    larp = models.BooleanField(default=False)

    zauber = models.PositiveIntegerField(null=True, blank=True)
    ap = models.PositiveIntegerField(null=True, blank=True)
    sp = models.PositiveIntegerField(null=True, blank=True)
    fp = models.PositiveIntegerField(null=True, blank=True)
    fg = models.PositiveIntegerField(null=True, blank=True)
    geld = models.PositiveIntegerField(null=True, blank=True)
    ip = models.IntegerField(default=0, blank=True)

    HPplus = models.IntegerField(default=0, blank=True)
    HPplus_fix = models.IntegerField(default=None, null=True, blank=True)

    gfs = models.ForeignKey("character.Gfs", on_delete=models.SET_NULL, null=True)
    profession = models.ForeignKey("character.Profession", on_delete=models.SET_NULL, null=True)
    attribute = models.ManyToManyField("character.Attribut", through="NewCharakterAttribut")
    fertigkeiten = models.ManyToManyField("character.Fertigkeit", through="NewCharakterFertigkeit")

    vorteile = models.ManyToManyField("character.Vorteil", through="NewCharakterVorteil")
    nachteile = models.ManyToManyField("character.Nachteil", through="NewCharakterNachteil")
    talente = models.ManyToManyField("character.Talent", through="NewCharakterTalent")

    spezial = models.ManyToManyField("character.Spezialfertigkeit", through="NewCharakterSpezialfertigkeit")
    wissen = models.ManyToManyField("character.Wissensfertigkeit", through="NewCharakterWissensfertigkeit")

    gratis_zauber = models.ManyToManyField("shop.Zauber", through="NewCharakterZauber")


class NewCharakterAttribut(models.Model):
    class Meta:
        ordering = ['char', 'attribut']
        verbose_name = "Startattribut"
        verbose_name_plural = "Startattribute"
        unique_together = ["attribut", "char"]

    attribut = models.ForeignKey('character.Attribut', on_delete=models.CASCADE)
    char = models.ForeignKey(NewCharakter, on_delete=models.CASCADE)

    aktuellerWert = models.PositiveIntegerField(default=0)
    aktuellerWert_ap = models.PositiveIntegerField(default=0)
    aktuellerWert_bonus = models.PositiveIntegerField(default=0)

    maxWert = models.PositiveIntegerField(default=0)
    maxWert_ap = models.PositiveIntegerField(default=0)
    maxWert_bonus = models.PositiveIntegerField(default=0)

    fg = models.PositiveIntegerField(default=0)
    fg_bonus = models.PositiveIntegerField(default=0)

    def ges_aktuell(self):
        return self.aktuellerWert + self.aktuellerWert_ap

    def ges_aktuell_bonus(self):
        return self.aktuellerWert + self.aktuellerWert_ap + self.aktuellerWert_bonus

    def ges_max(self):
        return self.maxWert + self.maxWert_ap

    def ges_max_bonus(self):
        return self.maxWert + self.maxWert_ap + self.maxWert_bonus

    def ges_fg(self):
        return self.fg

    def limit_fg(self):
        return min(self.ges_aktuell_bonus(), 12)


class NewCharakterFertigkeit(models.Model):
    class Meta:
        ordering = ["char", "fertigkeit"]
        verbose_name = "Startfertigkeit"
        verbose_name_plural = "Startfertigkeiten"
        unique_together = ["fertigkeit", "char"]

    fertigkeit = models.ForeignKey('character.Fertigkeit', on_delete=models.CASCADE)
    char = models.ForeignKey(NewCharakter, on_delete=models.CASCADE)

    fp = models.SmallIntegerField(default=0)
    fp_bonus = models.SmallIntegerField(default=0)

    def ges_fp(self):
        return self.fp + self.fp_bonus

    def ges_fg(self):
        if self.fertigkeit.attr2 is not None:
            return None
        return get_object_or_404(NewCharakterAttribut, char=self.char, attribut=self.fertigkeit.attr1).ges_fg()


class NewCharakterTeil(models.Model):
    """super for NewCharakterVor- & Nachteil"""
    class Meta:
        abstract = True
        ordering = ['char', 'teil']
        unique_together = ["teil", "char", "extra", "notizen"]

    char = models.ForeignKey(NewCharakter, on_delete=models.CASCADE)
    teil = None

    anzahl = models.PositiveSmallIntegerField(default=1)
    notizen = models.CharField(max_length=200, default="", blank=True)


class NewCharakterVorteil(NewCharakterTeil):
    class Meta:
        verbose_name = "Vorteil"
        verbose_name_plural = "Vorteile"

    teil = models.ForeignKey('character.Vorteil', on_delete=models.CASCADE)


class NewCharakterNachteil(NewCharakterTeil):
    class Meta:
        verbose_name = "Nachteil"
        verbose_name_plural = "Nachteile"

    teil = models.ForeignKey('character.Nachteil', on_delete=models.CASCADE)


class NewCharakterSpezialfertigkeit(models.Model):
    class Meta:
        ordering = ['char', 'spezialfertigkeit']
        verbose_name = "Spezialfertigkeit"
        verbose_name_plural = "Spezialfertigkeiten"
        unique_together = ["spezialfertigkeit", "char"]

    spezialfertigkeit = models.ForeignKey('character.Spezialfertigkeit', on_delete=models.CASCADE)
    char = models.ForeignKey(NewCharakter, on_delete=models.CASCADE)

    stufe = models.PositiveIntegerField(default=0, blank=True)


class NewCharakterWissensfertigkeit(models.Model):
    class Meta:
        ordering = ['char', 'wissensfertigkeit']
        verbose_name = "Wissensfertigkeit"
        verbose_name_plural = "Wissensfertigkeiten"
        unique_together = ["wissensfertigkeit", "char"]

    wissensfertigkeit = models.ForeignKey('character.Wissensfertigkeit', on_delete=models.CASCADE)
    char = models.ForeignKey(NewCharakter, on_delete=models.CASCADE)

    stufe = models.PositiveIntegerField(default=0, blank=True)


class NewCharakterTalent(models.Model):
    class Meta:
        ordering = ['char', 'talent']
        verbose_name = "Starttalent"
        verbose_name_plural = "Starttalente"
        unique_together = ["talent", "char"]

    talent = models.ForeignKey('character.Talent', on_delete=models.CASCADE)
    char = models.ForeignKey(NewCharakter, on_delete=models.CASCADE)


class NewCharakterZauber(models.Model):
    class Meta:
        ordering = ['item']
        verbose_name = "Gratiszauber"
        verbose_name_plural = "Gratiszauber"
        unique_together = ["item", "char"]

    item = models.ForeignKey("shop.Zauber", on_delete=models.CASCADE)
    char = models.ForeignKey(NewCharakter, on_delete=models.CASCADE)



priority_enum = [
    ('A', 'A'),
    ('B', 'B'),
    ('C', 'C'),
    ('D', 'D'),
    ('E', 'E'),
    ('F', 'F'),
]
class Priotable(models.Model):

    class Meta:
        ordering = ['priority']
        verbose_name = "Priotable Zeile"
        verbose_name_plural = "Priotable Zeilen"

    priority = models.CharField(choices=priority_enum, null=False, unique=True, max_length=1)
    ip = models.PositiveSmallIntegerField(default=0, null=False)
    ap = models.PositiveSmallIntegerField(default=0, null=False)
    sp = models.PositiveSmallIntegerField(default=0, null=False)
    fp = models.PositiveSmallIntegerField(default=0, null=False)
    fg = models.PositiveSmallIntegerField(default=0, null=False)
    zauber = models.PositiveSmallIntegerField(default=0, null=False)
    drachmen = models.PositiveIntegerField(default=0, null=False)

    def __str__(self):
        return "Priotable row {}".format(self.get_priority_display())


yes_neutral_no_enum = [
    ("y", "gut"),
    ("m", "durchschnittlich"),
    ("n", "schlecht")
]
alive_dead_enum = [
    ("l", "lebend"),
    ("t", "tot oder untot")
]
attitude_enum = [
    ("g", "gut"),
    ("n", "neutral"),
    ("e", "böse")
]
class GfsCharacterization(models.Model):
    class Meta:
        ordering = ['gfs']
        verbose_name = "Gfs Charakterisierung"
        verbose_name_plural = "Gfs Charakterisierungen"

    gfs = models.OneToOneField(Gfs, on_delete=models.CASCADE)
    state = models.CharField(help_text=".. lebend oder (un)tot sein?", choices=alive_dead_enum, null=True, max_length=1)
    social = models.CharField(help_text=".. sozial/umgänglich sein?", choices=yes_neutral_no_enum, null=True, max_length=1)
    magical = models.CharField(help_text=".. magisch sein?", choices=yes_neutral_no_enum, null=True, max_length=1)
    can_punch = models.CharField(help_text=".. Nahkampf haben?", choices=yes_neutral_no_enum, null=True, max_length=1)
    can_shoot = models.CharField(help_text=".. Fernkampf haben?", choices=yes_neutral_no_enum, null=True, max_length=1)
    gets_pricy_skills = models.CharField(help_text=".. krasse (dafür teure) Fähigkeiten bekommen?", choices=yes_neutral_no_enum, null=True, max_length=1)
    can_fly = models.CharField(help_text=".. fliegen können?", choices=yes_neutral_no_enum, null=True, max_length=1)
    attitude = models.CharField(help_text=".. gut/neutral/böse gesinnt sein?", choices=attitude_enum, null=True, max_length=1)

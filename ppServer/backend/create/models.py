from django.db import models

from character.models import Gfs


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
    cost = models.PositiveSmallIntegerField(default=0, null=False)

    ip = models.PositiveSmallIntegerField(default=0, null=False)
    ap = models.PositiveSmallIntegerField(default=0, null=False)
    sp = models.PositiveSmallIntegerField(default=0, null=False)
    konzentration = models.PositiveSmallIntegerField(default=0, null=False)
    fp = models.PositiveSmallIntegerField(default=0, null=False)
    fg = models.PositiveSmallIntegerField(default=0, null=False)
    zauber = models.PositiveSmallIntegerField(default=0, null=False)
    drachmen = models.PositiveIntegerField(default=0, null=False)
    spF_wF = models.PositiveIntegerField(default=0, null=False, verbose_name="Anz. Sp-F und Wissens-F.")

    def __str__(self):
        return "Priotable row {}".format(self.priority)


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
    state = models.CharField(verbose_name=".. lebend oder (un)tot sein?", choices=alive_dead_enum, null=True, blank=True, max_length=1)
    social = models.CharField(verbose_name=".. sozial/umgänglich sein?", choices=yes_neutral_no_enum, null=True, blank=True, max_length=1)
    magical = models.CharField(verbose_name=".. magisch sein?", choices=yes_neutral_no_enum, null=True, blank=True, max_length=1)
    can_punch = models.CharField(verbose_name=".. Nahkampf haben?", choices=yes_neutral_no_enum, null=True, blank=True, max_length=1)
    can_shoot = models.CharField(verbose_name=".. Fernkampf haben?", choices=yes_neutral_no_enum, null=True, blank=True, max_length=1)
    gets_pricy_skills = models.CharField(verbose_name=".. krasse (dafür teure) Fähigkeiten bekommen?", choices=yes_neutral_no_enum, null=True, blank=True, max_length=1)
    can_fly = models.CharField(verbose_name=".. fliegen können?", choices=yes_neutral_no_enum, null=True, blank=True, max_length=1)
    attitude = models.CharField(verbose_name=".. gut/neutral/böse gesinnt sein?", choices=attitude_enum, null=True, blank=True, max_length=1)

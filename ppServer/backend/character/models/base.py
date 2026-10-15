from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator
from django.db import models
from django.db.models.query import QuerySet
from django.utils.translation import gettext as _

from .. import enums
from ..permissions import CustomPermission


class Spieler(models.Model):

    class Meta:
        ordering = ['user']
        verbose_name_plural = "Spieler"
        permissions = [
            (CustomPermission.LARP.value.split(".")[-1], _("nimmt am LARP teil")),
            (CustomPermission.SPIELLEITUNG.value.split(".")[-1], _("leitet PnP-Runden und übernimmt Admin-Zeugs")),
            (CustomPermission.COPY_CHARS.value.split(".")[-1], _("überträgt alte Charaktere ohne Erstellung")),
            (CustomPermission.SEES_CALENDAR.value.split(".")[-1], _("sieht Lilly's Kalender")),
        ]

    LANGUAGE_ENUM = [
        ('g', 'Gemeinsprache'),
        ('d', 'Dämonisch'),
        ('e', 'Hochelfisch'),
    ]

    user = models.OneToOneField(get_user_model(), on_delete=models.CASCADE, blank=False, null=False)
    geburtstag = models.DateField(null=True, blank=True)

    language = models.CharField(max_length=1, choices=LANGUAGE_ENUM, default=LANGUAGE_ENUM[0][0], verbose_name="Sprache")

    class PreloadUserManager(models.Manager):
        def get_queryset(self) -> QuerySet:
            """ adds 'user' field """
            return super().get_queryset().prefetch_related("user")
    objects = PreloadUserManager()

    def __str__(self):
        """ shown e.g. in dropdown as foreign key """
        return self.user.get_full_name() or self.user.username


class Wesenkraft(models.Model):
    class Meta:
        ordering = ['titel']
        verbose_name = "Wesenkraft"
        verbose_name_plural = "Wesenkräfte"

    titel = models.CharField(max_length=30, null=False, default="")
    probe = models.CharField(max_length=200, null=False, default="")
    wirkung = models.TextField(null=False, default="")
    manaverbrauch = models.CharField(max_length=100, null=True, blank=True, default="")

    def __str__(self):
        return self.titel


class Persönlichkeit(models.Model):
    
    class Meta:
        ordering = ['titel']
        verbose_name = "Persönlichkeit"
        verbose_name_plural = "Persönlichkeiten"

    titel = models.CharField(max_length=64, unique=True)
    beschreibung = models.TextField()
    charakterbeispiele = models.TextField()

    def __str__(self):
        return self.titel


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
    has_implementation = models.BooleanField(default=False, verbose_name="ist implementiert")

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

    def __str__(self):
        return self.titel


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

import random, string
from datetime import date

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.shortcuts import get_object_or_404

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
        return name


class Wesenkraft(models.Model):
    class Meta:
        ordering = ['titel']
        verbose_name = "Wesenkraft"
        verbose_name_plural = "Wesenkräfte"

    titel = models.CharField(max_length=30, null=False, default="")
    probe = models.CharField(max_length=200, null=False, default="")
    wirkung = models.CharField(max_length=300, null=False, default="")
    min_rang = models.PositiveIntegerField(default=0)

    wesen = models.CharField(max_length=1, choices=enums.enum_wesenkr, null=False, default=enums.enum_wesenkr[0][0])
    zusatz_wesenspezifisch = models.ManyToManyField("Spezies", blank=True)
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
    beschreibung = models.TextField(max_length=3000, blank=True, default='')

    attribute = models.ManyToManyField('Attribut', through='SpeziesAttribut')

    def __str__(self):
        return self.titel

    def relAttributQueryset(self):
        return SpeziesAttribut.objects.filter(spezies=self)


class Gfs(models.Model):

    class Meta:
        ordering = ['wesen', 'titel']
        verbose_name = "Gfs/Klasse"
        verbose_name_plural = "Gfs/Klassen"

    titel = models.CharField(max_length=30, unique=True)
    wesen = models.ForeignKey(Spezies, on_delete=models.SET_NULL, blank=True, null=True)
    beschreibung = models.TextField(max_length=3000, blank=True, default='')

    ap = models.PositiveIntegerField(default=0, validators=[MaxValueValidator(100)])

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

    def __str__(self):
        return "{} ({})".format(self.titel, self.wesen.titel if self.wesen else "-")

    def relAttributQueryset(self):
        return GfsAttribut.objects.filter(gfs=self)

    def relVorteilQueryset(self):
        return GfsVorteil.objects.filter(gfs=self)

    def relNachteilQueryset(self):
        return GfsNachteil.objects.filter(gfs=self)

    # return list of all calculated attributes for a gfs
    def attr_calc(self):
        attr = []
        gfsAttrs = GfsAttribut.objects.filter(gfs=self)
        for gfsAttr in gfsAttrs:
            if self.wesen:
                wesenAttr = get_object_or_404(SpeziesAttribut, attribut__id=gfsAttr.attribut.id, spezies=self.wesen)
                entry = {'id': gfsAttr.attribut.id,
                         'aktuellerWert': gfsAttr.aktuellerWert + wesenAttr.aktuellerWert,
                         'maxWert': gfsAttr.maxWert + wesenAttr.maxWert}
            else:
                entry = {'id': gfsAttr.attribut.id,
                         'aktuellerWert': gfsAttr.aktuellerWert,
                         'maxWert': gfsAttr.maxWert}
            attr.append(entry)
        return attr


class Profession(models.Model):

    class Meta:
        ordering = ['titel']
        verbose_name = "Profession"
        verbose_name_plural = "Professionen"

    titel = models.CharField(max_length=30, unique=True)
    beschreibung = models.TextField(max_length=3000, blank=True, default='')

    attribute = models.ManyToManyField('Attribut', through='ProfessionAttribut')
    fertigkeiten = models.ManyToManyField("Fertigkeit", through="ProfessionFertigkeit")

    talente = models.ManyToManyField("Talent", through="ProfessionTalent")
    spezial = models.ManyToManyField("Spezialfertigkeit", through="ProfessionSpezialfertigkeit")
    wissen = models.ManyToManyField("Wissensfertigkeit", through="ProfessionWissensfertigkeit")

    def __str__(self):
        return self.titel

    def relAttributQueryset(self):
        return ProfessionAttribut.objects.filter(profession=self)


class SpeziesAttribut(models.Model):
    class Meta:
        ordering = ['attribut']
        verbose_name = "Startattribut"
        verbose_name_plural = "Startattribute"
        unique_together = ["attribut", "spezies"]

    attribut = models.ForeignKey('Attribut', on_delete=models.CASCADE)
    spezies = models.ForeignKey(Spezies, on_delete=models.CASCADE)

    aktuellerWert = models.PositiveIntegerField(default=0)
    maxWert = models.PositiveIntegerField(default=0)


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


class ProfessionAttribut(models.Model):
    class Meta:
        ordering = ['attribut']
        verbose_name = "Startattribut"
        verbose_name_plural = "Startattribute"
        unique_together = ["attribut", "profession"]

    attribut = models.ForeignKey('Attribut', on_delete=models.CASCADE)
    profession = models.ForeignKey(Profession, on_delete=models.CASCADE)

    aktuellerWert = models.IntegerField(default=0)
    maxWert = models.IntegerField(default=0)

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
        return "'{}' von ’{}’".format(self.fertigkeit.__str__(), self.profession.__str__())


class ProfessionSpezialfertigkeit(models.Model):

    class Meta:
        ordering = ['profession', 'spezial']
        verbose_name = "Startspezialfertigkeit"
        verbose_name_plural = "Startspezialfertigkeiten"

        unique_together = (('profession', 'spezial'),)

    profession = models.ForeignKey(Profession, on_delete=models.CASCADE)
    spezial = models.ForeignKey("Spezialfertigkeit", on_delete=models.CASCADE)

    def __str__(self):
        return "'{}' von ’{}’".format(self.spezial.__str__(), self.profession.__str__())


class ProfessionWissensfertigkeit(models.Model):

    class Meta:
        ordering = ['profession', 'wissen']
        verbose_name = "Startwissensfertigkeit"
        verbose_name_plural = "Startwissensfertigkeiten"

        unique_together = (('profession', 'wissen'),)

    profession = models.ForeignKey(Profession, on_delete=models.CASCADE)
    wissen = models.ForeignKey("Wissensfertigkeit", on_delete=models.CASCADE)

    def __str__(self):
        return "'{}' von ’{}’".format(self.wissen.__str__(), self.profession.__str__())


class ProfessionTalent(models.Model):
    class Meta:
        ordering = ['profession']
        verbose_name = "Starttalent"
        verbose_name_plural = "Starttalente"
        unique_together = ["profession", "talent"]

    talent = models.ForeignKey('Talent', on_delete=models.CASCADE)
    profession = models.ForeignKey(Profession, on_delete=models.CASCADE)


# TODO delete later
class Stufenplan(models.Model):
    class Meta:
        ordering = ['wesen', "stufe"]
        verbose_name = "Stufenplan"
        verbose_name_plural = "Stufenpläne"
        unique_together = ["wesen", "stufe"]

    wesen = models.ForeignKey(Spezies, on_delete=models.CASCADE)
    stufe = models.PositiveIntegerField(default=0)
    ep = models.PositiveIntegerField(default=0)

    vorteile = models.ManyToManyField("Vorteil", blank=True)
    ap = models.PositiveSmallIntegerField(default=0)
    ap_max = models.PositiveSmallIntegerField(default=0)
    fp = models.PositiveSmallIntegerField(default=0)
    fg = models.PositiveSmallIntegerField(default=0)
    zauber = models.PositiveSmallIntegerField(default=0)
    wesenkräfte = models.ManyToManyField("Wesenkraft", blank=True)
    spezial = models.PositiveSmallIntegerField(default=0)
    wissensp = models.PositiveSmallIntegerField(default=0)
    weiteres = models.TextField(max_length=50, default=None, blank=True, null=True)


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
    weiteres = models.TextField(max_length=1000, default=None, blank=True, null=True)


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
    beschreibung = models.TextField(max_length=1000, blank=True, default="")
    wann_wählbar = models.CharField(max_length=1, choices=enums.teil_erstellung_enum, default=enums.teil_erstellung_enum[0][0])



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


class Begleiter(models.Model):
    class Meta:
        ordering = ['name']
        verbose_name = "Begleiter"
        verbose_name_plural = "Begleiter"

    name = models.CharField(max_length=200, default='', unique=True)
    beschreibung = models.CharField(max_length=100, blank=True, default='')

    def __str__(self):
        return "{}".format(self.name)


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
    name = models.CharField(max_length=200, default=rand_str, blank=True, unique=True)
    spezies = models.ManyToManyField(Spezies, related_name='wesen', through='RelSpezies')
    gfs = models.ForeignKey(Gfs, on_delete=models.SET_NULL, null=True, blank=True)
    profession = models.ForeignKey(Profession, on_delete=models.SET_NULL, null=True, blank=True)

    manifest = models.DecimalField('Startmanifest', max_digits=4, decimal_places=2, default=10.0,
                                   validators=[MaxValueValidator(10), MinValueValidator(0)])
    sonstiger_manifestverlust = models.DecimalField("sonstiger Manifestverlust", max_digits=4, decimal_places=2, default=0.0,
                                                    validators=[MaxValueValidator(10), MinValueValidator(0)], blank=True)
    notizen_sonstiger_manifestverlust = models.CharField(max_length=200, default="", blank=True)

    gewicht = models.PositiveIntegerField(default=75, blank=True)
    größe = models.PositiveIntegerField(default=170, blank=True)
    alter = models.PositiveIntegerField(default=0, blank=True)
    geschlecht = models.CharField(max_length=100, blank=True)
    sexualität = models.CharField(max_length=100, blank=True)
    beruf = models.ForeignKey(Beruf, null=True, on_delete=models.SET_NULL, blank=True)
    präf_arm = models.CharField(max_length=100, default="", blank=True)
    religion = models.ForeignKey(Religion, null=True, on_delete=models.SET_NULL, blank=True)
    hautfarbe = models.CharField(max_length=100, default="", blank=True)
    haarfarbe = models.CharField(max_length=100, default="", blank=True)
    augenfarbe = models.CharField(max_length=100, default="", blank=True)

    nutzt_magie = models.PositiveSmallIntegerField(choices=enums.nutzt_magie_enum, default=enums.nutzt_magie_enum[0][0], blank=True)
    useEco = models.BooleanField("benutze 'eco':y, benutze 'morph':n", default=True, blank=True)

    eco = models.PositiveIntegerField(default=0, blank=True)
    morph = models.PositiveIntegerField(default=0, blank=True)
    sp = models.PositiveIntegerField(default=0)
    ip = models.IntegerField(default=0)
    tp = models.IntegerField(default=0)
    geld = models.IntegerField(default=0)

    ep = models.PositiveIntegerField(default=0)

    HPplus = models.IntegerField(default=0, blank=True)
    HPplus_fix = models.IntegerField(default=None, null=True, blank=True)
    wesenschaden_waff_kampf = models.IntegerField(default=0)
    wesenschaden_andere_gestalt = models.IntegerField("BS andere Gestalt", blank=True, null=True)
    rang = models.PositiveIntegerField(default=0, validators=[MaxValueValidator(500)], blank=True)

    vorteile = models.ManyToManyField(Vorteil, through="RelVorteil", blank=True)
    nachteile = models.ManyToManyField(Nachteil, through="RelNachteil", blank=True)
    talente = models.ManyToManyField(Talent, through="RelTalent", blank=True)

    notizen = models.TextField(blank=True)
    persönlicheZiele = models.TextField(blank=True)

    wesenkräfte = models.ManyToManyField(Wesenkraft, through="RelWesenkraft", blank=True)
    verwandlungen = models.ManyToManyField(Spezies, related_name='verwandlungen', blank=True)

    attribute = models.ManyToManyField(Attribut, through='RelAttribut', blank=True)
    fertigkeiten = models.ManyToManyField(Fertigkeit, through='RelFertigkeit', blank=True)
    spezialfertigkeiten = models.ManyToManyField(Spezialfertigkeit, through='RelSpezialfertigkeit', blank=True)
    wissensfertigkeiten = models.ManyToManyField(Wissensfertigkeit, through='RelWissensfertigkeit', blank=True)

    begleiter = models.ManyToManyField(Begleiter, through='RelBegleiter', blank=True)

    items = models.ManyToManyField('shop.Item', through='RelItem', blank=True)
    waffenWerkzeuge = models.ManyToManyField('shop.Waffen_Werkzeuge', through='RelWaffen_Werkzeuge', blank=True)
    magazine = models.ManyToManyField('shop.Magazin', through='RelMagazin', blank=True)
    schusswaffen = models.ManyToManyField('shop.Schusswaffen', through='RelSchusswaffen', blank=True)
    magischeAusrüstung = models.ManyToManyField('shop.Magische_Ausrüstung', through='RelMagische_Ausrüstung', blank=True)
    rituale_runen = models.ManyToManyField('shop.Rituale_Runen', through='RelRituale_Runen', blank=True)
    rüstungen = models.ManyToManyField('shop.Rüstungen', through='RelRüstung', blank=True)
    ausrüstungTechnik = models.ManyToManyField('shop.Ausrüstung_Technik', through='RelAusrüstung_Technik', blank=True)
    fahrzeuge = models.ManyToManyField('shop.Fahrzeug', through='RelFahrzeug', blank=True)
    einbauten = models.ManyToManyField('shop.Einbauten', through='RelEinbauten', blank=True)
    zauber = models.ManyToManyField('shop.Zauber', through='RelZauber', blank=True)

    sonstige_items = models.TextField(max_length=1000, default='', blank=True)

    def __str__(self):
        return "{} ({})".format(self.name, self.eigentümer)

    def HP_plus_(self):
        return self.HPplus



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


class RelBegleiter(models.Model):

    class Meta:
        ordering = ['char', 'begleiter']
        verbose_name = "Begleiter"
        verbose_name_plural = "Begleiter"

        unique_together = (('char', 'begleiter'),)

    char = models.ForeignKey(Charakter, on_delete=models.CASCADE)
    begleiter = models.ForeignKey(Begleiter, on_delete=models.CASCADE)
    status = models.CharField(max_length=60, choices=enums.status_enum)
    notizen = models.CharField(max_length=100, blank=True, default='')

    def __str__(self):
        return "'{}' von Charakter '{}'".format(self.begleiter, self.char)


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
    notizen = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return "'{}' zu Charakter '{}'".format(self.teil.titel, self.char.name)


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
    aktuellerWert_bonus = models.PositiveIntegerField(default=0)

    maxWert = models.PositiveIntegerField(default=0)
    maxWert_bonus = models.PositiveIntegerField(default=0)

    fg = models.PositiveIntegerField(default=0)
    fg_bonus = models.PositiveIntegerField(default=0)

    def __str__(self):
        return "'{}' von '{}'".format(self.attribut.__str__(), self.char.__str__())

    def aktuell(self): return self.aktuellerWert + self.aktuellerWert_bonus
    def max(self): return self.maxWert + self.maxWert_bonus
    def fg_sum(self): return self.fg + self.fg_bonus

class RelFertigkeit(models.Model):

    class Meta:
        ordering = ['char', 'fertigkeit']
        verbose_name = "Fertigkeit"
        verbose_name_plural = "Fertigkeiten"

        unique_together = (('char', 'fertigkeit'),)

    char = models.ForeignKey(Charakter, on_delete=models.CASCADE)
    fertigkeit = models.ForeignKey(Fertigkeit, on_delete=models.CASCADE)

    fp = models.SmallIntegerField(default=0)
    fp_bonus = models.SmallIntegerField(default=0)

    def __str__(self):
        return "'{}' von ’{}’".format(self.fertigkeit.__str__(), self.char.__str__())

    def pool(self):
        pool = self.fp + self.fp_bonus
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

    item = models.ForeignKey('shop.Item', on_delete=models.CASCADE)


class RelWaffen_Werkzeuge(RelShop):
    class Meta:
        verbose_name = "Waffe/Werkzeug"
        verbose_name_plural = "Waffen & Werkzeuge"

    item = models.ForeignKey('shop.Waffen_Werkzeuge', on_delete=models.CASCADE)


class RelMagazin(RelShop):
    class Meta:
        verbose_name = "Magazin"
        verbose_name_plural = "Magazine"

    item = models.ForeignKey('shop.Magazin', on_delete=models.CASCADE)


class RelPfeil_Bolzen(RelShop):
    class Meta:
        verbose_name = "Pfeil/Bolzen"
        verbose_name_plural = "Pfeile & Bolzen"

    item = models.ForeignKey('shop.Pfeil_bolzen', on_delete=models.CASCADE)


class RelSchusswaffen(RelShop):
    class Meta:
        verbose_name = "Schusswaffe"
        verbose_name_plural = "Schusswaffen"

    item = models.ForeignKey('shop.Schusswaffen', on_delete=models.CASCADE)


class RelMagische_Ausrüstung(RelShop):
    class Meta:
        verbose_name = "magische Ausrüstung"
        verbose_name_plural = "magische Ausrüstung"

    item = models.ForeignKey('shop.Magische_Ausrüstung', on_delete=models.CASCADE)


class RelRüstung(RelShop):
    class Meta:
        verbose_name = "Rüstung"
        verbose_name_plural = "Rüstungen"

    item = models.ForeignKey('shop.Rüstungen', on_delete=models.CASCADE)


class RelAusrüstung_Technik(RelShop):
    class Meta:
        verbose_name = "Ausrüstung & Technik"
        verbose_name_plural = "Ausrüstung & Technik"

    item = models.ForeignKey('shop.Ausrüstung_Technik', on_delete=models.CASCADE)
    selbst_eingebaut = models.BooleanField(default=False)


class RelFahrzeug(RelShop):
    class Meta:
        verbose_name = "Fahrzeug"
        verbose_name_plural = "Fahrzeuge"

    item = models.ForeignKey('shop.Fahrzeug', on_delete=models.CASCADE)


class RelEinbauten(RelShop):
    class Meta:
        verbose_name = "Einbauten"
        verbose_name_plural = "Einbauten"

    item = models.ForeignKey('shop.Einbauten', on_delete=models.CASCADE)


class RelZauber(RelShop):
    class Meta:
        verbose_name = "Zauber"
        verbose_name_plural = "Zauber"

    item = models.ForeignKey('shop.Zauber', on_delete=models.CASCADE)

    def __str__(self):
        return "{}".format(self.item)


class RelAlchemie(RelShop):
    class Meta:
        verbose_name = "Alchemie"
        verbose_name_plural = "Alchemie"

    item = models.ForeignKey('shop.Alchemie', on_delete=models.CASCADE)


class RelTinker(RelShop):
    class Meta:
        verbose_name = "Für Selbstständige"
        verbose_name_plural = "Für Selbstständige"

    item = models.ForeignKey('shop.Tinker', on_delete=models.CASCADE)


class RelRituale_Runen(RelShop):
    class Meta:
        verbose_name = "Ritual/Rune"
        verbose_name_plural = "Rituale & Runen"

    item = models.ForeignKey('shop.Rituale_Runen', on_delete=models.CASCADE)


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

    firma_shop = models.ForeignKey('shop.FirmaItem', on_delete=models.CASCADE)


class RelFirmaWaffen_Werkzeuge(RelFirmaShop):
    class Meta:
        verbose_name = "Waffe/Werkzeug Verfügbarkeit"
        verbose_name_plural = "Waffen & Werkzeuge Verfügbarkeiten"

    firma_shop = models.ForeignKey('shop.FirmaWaffen_Werkzeuge', on_delete=models.CASCADE)


class RelFirmaMagazin(RelFirmaShop):
    class Meta:
        verbose_name = "Magazin Verfügbarkeit"
        verbose_name_plural = "Magazine Verfügbarkeiten"

    firma_shop = models.ForeignKey('shop.FirmaMagazin', on_delete=models.CASCADE)


class RelFirmaPfeil_Bolzen(RelFirmaShop):
    class Meta:
        verbose_name = "Pfeil/Bolzen Verfügbarkeit"
        verbose_name_plural = "Pfeile & Bolzen Verfügbarkeiten"

    firma_shop = models.ForeignKey('shop.FirmaPfeil_bolzen', on_delete=models.CASCADE)


class RelFirmaSchusswaffen(RelFirmaShop):
    class Meta:
        verbose_name = "Schusswaffe Verfügbarkeit"
        verbose_name_plural = "Schusswaffen Verfügbarkeiten"

    firma_shop = models.ForeignKey('shop.FirmaSchusswaffen', on_delete=models.CASCADE)


class RelFirmaMagische_Ausrüstung(RelFirmaShop):
    class Meta:
        verbose_name = "magische Ausrüstung Verfügbarkeit"
        verbose_name_plural = "magische Ausrüstung Verfügbarkeiten"

    firma_shop = models.ForeignKey('shop.FirmaMagische_Ausrüstung', on_delete=models.CASCADE)


class RelFirmaRüstung(RelFirmaShop):
    class Meta:
        verbose_name = "Rüstung Verfügbarkeit"
        verbose_name_plural = "Rüstungen Verfügbarkeiten"

    firma_shop = models.ForeignKey('shop.FirmaRüstungen', on_delete=models.CASCADE)


class RelFirmaAusrüstung_Technik(RelFirmaShop):
    class Meta:
        verbose_name = "Ausrüstung & Technik Verfügbarkeit"
        verbose_name_plural = "Ausrüstung & Technik Verfügbarkeiten"

    firma_shop = models.ForeignKey('shop.FirmaAusrüstung_Technik', on_delete=models.CASCADE)


class RelFirmaFahrzeug(RelFirmaShop):
    class Meta:
        verbose_name = "Fahrzeug Verfügbarkeit"
        verbose_name_plural = "Fahrzeuge Verfügbarkeiten"

    firma_shop = models.ForeignKey('shop.FirmaFahrzeug', on_delete=models.CASCADE)


class RelFirmaEinbauten(RelFirmaShop):
    class Meta:
        verbose_name = "Einbauten Verfügbarkeit"
        verbose_name_plural = "Einbauten Verfügbarkeiten"

    firma_shop = models.ForeignKey('shop.FirmaEinbauten', on_delete=models.CASCADE)


class RelFirmaZauber(RelFirmaShop):
    class Meta:
        verbose_name = "Zauber Verfügbarkeit"
        verbose_name_plural = "Zauber Verfügbarkeiten"

    firma_shop = models.ForeignKey('shop.FirmaZauber', on_delete=models.CASCADE)

    def __str__(self):
        return "{}".format(self.firma_shop)


class RelFirmaAlchemie(RelFirmaShop):
    class Meta:
        verbose_name = "Alchemie Verfügbarkeit"
        verbose_name_plural = "Alchemie Verfügbarkeiten"

    firma_shop = models.ForeignKey('shop.FirmaAlchemie', on_delete=models.CASCADE)


class RelFirmaTinker(RelFirmaShop):
    class Meta:
        verbose_name = "Für Selbstständige Verfügbarkeit"
        verbose_name_plural = "Für Selbstständige Verfügbarkeiten"

    firma_shop = models.ForeignKey('shop.FirmaTinker', on_delete=models.CASCADE)


class RelFirmaRituale_Runen(RelFirmaShop):
    class Meta:
        verbose_name = "Ritual/Rune Verfügbarkeit"
        verbose_name_plural = "Rituale & Runen Verfügbarkeiten"

    firma_shop = models.ForeignKey('shop.FirmaRituale_Runen', on_delete=models.CASCADE)

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


class SkilltreeEntryWesen(models.Model):
    class Meta:
        unique_together = ["context", "wesen"]

    context = models.ForeignKey(SkilltreeBase, on_delete=models.CASCADE, null=True)

    wesen = models.ForeignKey(Spezies, on_delete=models.CASCADE, null=True)
    text = models.TextField(max_length=100)

    def __str__(self):
        return "{} (Stufe {})".format(self.wesen, self.context.stufe)


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

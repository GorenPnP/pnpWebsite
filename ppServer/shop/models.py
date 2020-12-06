import re

import math
from datetime import timedelta

from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.timezone import now
from django.db import models
from django.urls import reverse

from character.models import Spezialfertigkeit, Wissensfertigkeit

from .enums import *


# Firma
class Firma(models.Model):
    class Meta:
        ordering = ['name']
        verbose_name = "Firma"
        verbose_name_plural = "Firmen"

    name = models.CharField(max_length=50, default='')
    beschreibung = models.TextField(max_length=1000, default='', blank=True)

    price_factor = models.FloatField(default=1.0)

    def __str__(self):
        return "{}".format(self.name)


############# FirmaShop #####################

class FirmaShop(models.Model):
    class Meta:
        abstract = True
        ordering = ['item', 'firma']
        verbose_name = "Firma"
        verbose_name_plural = "Firmen"

    firma = models.ForeignKey(Firma, on_delete=models.CASCADE)
    preis = models.IntegerField(default=0, null=True)       # dont use this property, instead self.current_price()

    verfügbarkeit = models.PositiveIntegerField(default=0)

    def __str__(self):
        return "{} von {} ({}%)".format(self.item, self.firma, self.verfügbarkeit)

    def current_price(self):
        return math.floor(self.preis * self.firma.price_factor + .5)


class FirmaItem(FirmaShop):
    item = models.ForeignKey('Item', on_delete=models.CASCADE)


class FirmaWaffen_Werkzeuge(FirmaShop):
    item = models.ForeignKey('Waffen_Werkzeuge', on_delete=models.CASCADE)


class FirmaMagazin(FirmaShop):
    item = models.ForeignKey('Magazin', on_delete=models.CASCADE)


class FirmaPfeil_Bolzen(FirmaShop):
    item = models.ForeignKey('Pfeil_Bolzen', on_delete=models.CASCADE)


class FirmaSchusswaffen(FirmaShop):
    item = models.ForeignKey('Schusswaffen', on_delete=models.CASCADE)


class FirmaMagische_Ausrüstung(FirmaShop):
    item = models.ForeignKey('Magische_Ausrüstung', on_delete=models.CASCADE)


class FirmaRituale_Runen(models.Model):
    class Meta:
        verbose_name = "Firma"
        verbose_name_plural = "Firmen"

    firma = models.ForeignKey(Firma, on_delete=models.CASCADE)
    item = models.ForeignKey('Rituale_Runen', on_delete=models.CASCADE)

    stufe_1 = models.IntegerField(default=0, null=True)
    stufe_2 = models.IntegerField(default=0, null=True)
    stufe_3 = models.IntegerField(default=0, null=True)
    stufe_4 = models.IntegerField(default=0, null=True)
    stufe_5 = models.IntegerField(default=0, null=True)


    verfügbarkeit = models.PositiveIntegerField(default=0)

    def __str__(self):
        return "{} von {} ({}%)".format(self.item, self.firma, self.verfügbarkeit)

    def clean(self):
        if preis_lte(self.stufe_1, self.stufe_2) and \
            preis_lte(self.stufe_2, self.stufe_3) and \
            preis_lte(self.stufe_3, self.stufe_4) and \
                preis_lte(self.stufe_4, self.stufe_5):
            pass
        else:
            raise ValidationError("Höhere Stufe kostet weniger")


class FirmaRüstungen(FirmaShop):
    item = models.ForeignKey('Rüstungen', on_delete=models.CASCADE)


class FirmaAusrüstung_Technik(FirmaShop):
    item = models.ForeignKey('Ausrüstung_Technik', on_delete=models.CASCADE)


class FirmaFahrzeug(FirmaShop):
    item = models.ForeignKey('Fahrzeug', on_delete=models.CASCADE)


class FirmaEinbauten(FirmaShop):
    item = models.ForeignKey('Einbauten', on_delete=models.CASCADE)


class FirmaZauber(FirmaShop):
    item = models.ForeignKey('Zauber', on_delete=models.CASCADE)


class FirmaAlchemie(FirmaShop):
    item = models.ForeignKey('Alchemie', on_delete=models.CASCADE)


class FirmaTinker(FirmaShop):
    item = models.ForeignKey('Tinker', on_delete=models.CASCADE)

################ Base Shop ####################

class BaseShop(models.Model):
    class Meta:
        abstract = True
        ordering = ['name']

    name = models.CharField(max_length=50, default='', unique=True)
    beschreibung = models.TextField(max_length=1500, default='', blank=True)
    icon = models.ImageField(null=True, blank=True)

    ab_stufe = models.IntegerField(default=0, validators=[MinValueValidator(0)], blank=True)
    illegal = models.BooleanField(default=False)
    lizenz_benötigt = models.BooleanField(default=False)

    frei_editierbar = models.BooleanField(default=True)
    stufenabhängig = models.BooleanField(default=False)


    @staticmethod
    def get_fields():
        return [
            [{"val": "Name"}],
            [{"val": "Beschreibung"}],
            [{"val": "Ab Stufe"}],
            [{"val": "Günstigster Preis"}],
            [{"val": "Weiteres"}],
            [{"val": "Preis * Stufe?"}]
            ]

    def get_values(self, firma_model, url_prefix=None):

        weiteres = "illegal" if self.illegal else ""
        if self.lizenz_benötigt and not weiteres: weiteres = "Lizenz"
        if self.lizenz_benötigt and self.illegal: weiteres += ", Lizenz"

        offers = firma_model.objects.filter(item=self)
        billigster = sorted([o.current_price() for o in offers])[0] if offers.count() else None

        return [[{"val": self.name, "icon_url": self.getIconUrl(), "url": reverse(url_prefix, args=[self.id]), "name": self.id}],
                [{"val": self.beschreibung}],
                [{"val": self.ab_stufe}],
                [{"val": billigster}],
                [{"val": weiteres}],
                [{"val": "ja" if self.stufenabhängig else ""}]
                ]

    def getIconUrl(self):
        return self.icon.url if self.icon else "/static/res/img/icon-dice-account.svg"


class Item(BaseShop):
    class Meta:
        verbose_name = "Item"
        verbose_name_plural = "Items"

    kategorie = models.CharField(choices=item_enum, max_length=2, default=item_enum[0][0])
    firmen = models.ManyToManyField('Firma', through='FirmaItem', blank=True, related_name='firmen')

    def __str__(self):
        return "{} (item)".format(self.name)

    def get_values(self, firma_model=FirmaItem, url_prefix="shop:buy_item"):
        return super().get_values(firma_model, url_prefix)


class Waffen_Werkzeuge(BaseShop):
    class Meta:
        verbose_name = "Waffe/Werkzeug"
        verbose_name_plural = "Waffen & Werkzeuge"

    erfolge = models.PositiveIntegerField(default=0)
    bs = models.CharField(max_length=20, default=0)
    zs = models.CharField(max_length=20, default=0)
    dk = models.PositiveIntegerField(default=0, blank=True, null=True)

    kategorie = models.CharField(choices=werkzeuge_enum, max_length=2, default=werkzeuge_enum[0][0])
    firmen = models.ManyToManyField('Firma', through='FirmaWaffen_Werkzeuge', blank=True)

    def __str__(self):
        return "{} (Waffen & Werkzeuge)".format(self.name)

    @staticmethod
    def get_fields():
        return [
            [{"val": "Name"}],
            [{"val": "Beschreibung"}],
            [{"val": "Ab Stufe"}],
            [{"val": "Erfolge"}],
            [{"val": "BS"}],
            [{"val": "ZS"}],
            [{"val": "DK"}],
            [{"val": "Günstigster Preis"}],
            [{"val": "Weiteres"}],
            [{"val": "Preis * Stufe?"}]
        ]

    def get_values(self, firma_model=FirmaWaffen_Werkzeuge, url_prefix="shop:buy_waffen_werkzeuge"):
        fields = super().get_values(firma_model, url_prefix)

        return fields[:3] +\
            [
                [{"val": self.erfolge}],
                [{"val": self.bs}],
                [{"val": self.zs}],
                [{"val": self.dk}],
            ]\
            + fields[3:]


class Magazin(BaseShop):
    class Meta:
        verbose_name = "Magazin"
        verbose_name_plural = "Magazine"

    schuss = models.PositiveIntegerField(default=0)
    firmen = models.ManyToManyField('Firma', through='FirmaMagazin', blank=True)

    def __str__(self):
        return "{}, {} Schuss (Magazine)".format(self.name, self.schuss)

    @staticmethod
    def get_fields():

        return [
            [{"val": "Name"}],
            [{"val": "Beschreibung"}],
            [{"val": "Ab Stufe"}],
            [{"val": "Schuss"}],
            [{"val": "Günstigster Preis"}],
            [{"val": "Weiteres"}],
            [{"val": "Preis * Stufe?"}]
        ]

    def get_values(self, firma_model=FirmaMagazin, url_prefix="shop:buy_magazine"):
        fields = super().get_values(firma_model, url_prefix)
        return fields[:3] + [ [{"val": self.schuss}] ] + fields[3:]


class Pfeil_Bolzen(BaseShop):
    class Meta:
        verbose_name = "Pfeil/Bolzen"
        verbose_name_plural = "Pfeile & Bolzen"

    bs = models.CharField(max_length=20, default='')
    zs = models.CharField(max_length=20, default='')
    firmen = models.ManyToManyField('Firma', through='FirmaPfeil_Bolzen', blank=True)

    def __str__(self):
        return "{} (Pfeile & Bolzen)".format(self.name)

    @staticmethod
    def get_fields():
        return [
            [{"val": "Name"}],
            [{"val": "Beschreibung"}],
            [{"val": "Ab Stufe"}],
            [{"val": "BS"}],
            [{"val": "ZS"}],
            [{"val": "Günstigster Preis"}],
            [{"val": "Weiteres"}],
            [{"val": "Preis * Stufe?"}]
        ]

    def get_values(self, firma_model=FirmaPfeil_Bolzen, url_prefix="shop:buy_pfeil_bolzen"):
        fields = super().get_values(firma_model, url_prefix)

        return fields[:3] +\
            [
                [{"val": self.bs}],
                [{"val": self.zs}]
            ] + fields[3:]


class Schusswaffen(BaseShop):
    class Meta:
        verbose_name = "Schusswaffe"
        verbose_name_plural = "Schusswaffen"

    erfolge = models.PositiveIntegerField(default=0)
    bs = models.CharField(max_length=20, default='')
    zs = models.CharField(max_length=20, default='')

    magazine = models.ManyToManyField(Magazin, blank=True)
    pfeile_bolzen = models.ManyToManyField(Pfeil_Bolzen, blank=True)

    dk = models.PositiveIntegerField(default=0, blank=True)
    präzision = models.PositiveIntegerField(default=0, blank=True)

    kategorie = models.CharField(choices=schusswaffen_enum, max_length=2, default=schusswaffen_enum[0][0])
    firmen = models.ManyToManyField('Firma', through='FirmaSchusswaffen', blank=True)

    def __str__(self):
        return "{} (Schusswaffen)".format(self.name)

    @staticmethod
    def get_fields():
        return [
            [{"val": "Name"}],
            [{"val": "Beschreibung"}],
            [{"val": "Ab Stufe"}],
            [{"val": "Erfolge"}],
            [{"val": "BS"}],
            [{"val": "ZS"}],
            [{"val": "Magazine"}],
            [{"val": "Pfeile & Bolzen"}],
            [{"val": "DK"}],
            [{"val": "Präzision"}],
            [{"val": "Günstigster Preis"}],
            [{"val": "Weiteres"}],
            [{"val": "Preis * Stufe?"}]
        ]

    def get_values(self, firma_model=FirmaSchusswaffen, url_prefix="shop:buy_schusswaffen"):
        fields = super().get_values(firma_model, url_prefix)
        magazin_url = reverse("shop:magazine")
        pf_bol_url = reverse("shop:pfeile_bolzen")

        return fields[:3] +\
            [
                [{"val": self.erfolge}],
                [{"val": self.bs}],
                [{"val": self.zs}],
                [{"val": i.name, "url": "{}#{}".format(magazin_url, i.id)} for i in self.magazine.all()],
                [{"val": i.name, "url": "{}#{}".format(pf_bol_url, i.id)} for i in self.pfeile_bolzen.all()],
                [{"val": self.dk}],
                [{"val": self.präzision}],
            ] + fields[3:]


class Magische_Ausrüstung(BaseShop):
    class Meta:
        verbose_name = "magische Ausrüstung"
        verbose_name_plural = "magische Ausrüstung"

    kategorie = models.CharField(choices=magische_Ausrüstung_enum, max_length=2, default=magische_Ausrüstung_enum[0][0])
    firmen = models.ManyToManyField('Firma', through='FirmaMagische_Ausrüstung', blank=True)

    def __str__(self):
        return "{} (Magische Ausrüstung)".format(self.name)

    def get_values(self, firma_model=FirmaMagische_Ausrüstung, url_prefix="shop:buy_mag_ausrüstung"):
        return super().get_values(firma_model, url_prefix)


class Rituale_Runen(BaseShop):
    class Meta:
        verbose_name = "Ritual/Rune"
        verbose_name_plural = "Rituale & Runen"

    kategorie = models.CharField(choices=rituale_enum, max_length=2, default=rituale_enum[0][0])
    firmen = models.ManyToManyField('Firma', through='FirmaRituale_Runen', blank=True)

    def __str__(self):
        return "{} (Rituale & Runen)".format(self.name)

    @staticmethod
    def get_fields():
        return [
            [{"val": "Name"}],
            [{"val": "Beschreibung"}],
            [{"val": "Ab Stufe"}],
            [{"val": "Günstigster Preis für Stufe 1"}],
            [{"val": "... für Stufe 2"}],
            [{"val": "... für Stufe 3"}],
            [{"val": "... für Stufe 4"}],
            [{"val": "... für Stufe 5"}],
            [{"val": "Weiteres"}],
            [{"val": "Preis * Stufe?"}]
        ]

    def get_values(self, firma_model=FirmaRituale_Runen, url_prefix="shop:buy_rituale_runen"):

        weiteres = "illegal" if self.illegal else ""
        if self.lizenz_benötigt and not weiteres:
            weiteres = "Lizenz"
        if self.lizenz_benötigt and self.illegal:
            weiteres += ", Lizenz"

        offers1 = firma_model.objects.filter(item=self).order_by("stufe_1")
        billig1 = offers1[0].stufe_1 if offers1.count() else None

        offers2 = firma_model.objects.filter(item=self).order_by("stufe_2")
        billig2 = offers2[0].stufe_2 if offers2.count() else None

        offers3 = firma_model.objects.filter(item=self).order_by("stufe_3")
        billig3 = offers3[0].stufe_3 if offers3.count() else None

        offers4 = firma_model.objects.filter(item=self).order_by("stufe_4")
        billig4 = offers4[0].stufe_4 if offers4.count() else None

        offers5 = firma_model.objects.filter(item=self).order_by("stufe_5")
        billig5 = offers5[0].stufe_5 if offers5.count() else None

        return [[{"val": self.name, "icon_url": self.getIconUrl(), "url": reverse(url_prefix, args=[self.id])}],
                [{"val": self.beschreibung}],
                [{"val": self.ab_stufe}],
                [{"val": billig1}],
                [{"val": billig2}],
                [{"val": billig3}],
                [{"val": billig4}],
                [{"val": billig5}],
                [{"val": weiteres}],
                [{"val": "ja" if self.stufenabhängig else ""}]
                ]


class Rüstungen(BaseShop):
    class Meta:
        verbose_name = "Rüstung"
        verbose_name_plural = "Rüstung"

    schutz = models.PositiveIntegerField(default=0)
    stärke = models.PositiveIntegerField(default=0)
    haltbarkeit = models.PositiveIntegerField(default=0)

    firmen = models.ManyToManyField('Firma', through='FirmaRüstungen', blank=True)

    def __str__(self):
        return "{} (Rüstungen)".format(self.name)

    @staticmethod
    def get_fields():
        return [
            [{"val": "Name"}],
            [{"val": "Beschreibung"}],
            [{"val": "Ab Stufe"}],
            [{"val": "Schutz"}],
            [{"val": "Stärke"}],
            [{"val": "Haltbarkeit"}],
            [{"val": "Günstigster Preis"}],
            [{"val": "Weiteres"}],
            [{"val": "Preis * Stufe?"}]
        ]

    def get_values(self, firma_model=FirmaMagische_Ausrüstung, url_prefix="shop:buy_rüstungen"):
        fields = super().get_values(firma_model, url_prefix)

        return fields[:3] +\
            [
                [{"val": self.schutz}],
                [{"val": self.stärke}],
                [{"val": self.haltbarkeit}]
            ] + fields[3:]


class Ausrüstung_Technik(BaseShop):
    class Meta:
        verbose_name = "Ausrüstung/Technik"
        verbose_name_plural = "Ausrüstung & Technik"

    manifestverlust_str = models.CharField(max_length=20, null=True, blank=True)
    manifestverlust = models.DecimalField('manifestverlust', max_digits=4, decimal_places=2,
                                          default=0.0, blank=True, null=True,
                                          validators=[MinValueValidator(0), MaxValueValidator(10)])
    kategorie = models.CharField(choices=ausrüstung_enum, max_length=2, default=ausrüstung_enum[0][0])
    firmen = models.ManyToManyField('Firma', through='FirmaAusrüstung_Technik', blank=True)

    def __str__(self):
        return "{} (Ausrüstung & Technik)".format(self.name)

    def get_values(self, firma_model=FirmaAusrüstung_Technik, url_prefix="shop:buy_ausrüstung_technik"):
        return super().get_values(firma_model, url_prefix)


class Fahrzeug(BaseShop):
    class Meta:
        verbose_name = "Fahrzeug"
        verbose_name_plural = "Fahrzeuge"

    schnelligkeit = models.PositiveIntegerField(blank=True, null=True)
    rüstung = models.PositiveIntegerField(blank=True, null=True)
    erfolge = models.PositiveIntegerField(default=0, blank=True, null=True)

    kategorie = models.CharField(choices=fahrzeuge_enum, max_length=2, default=fahrzeuge_enum[0][0])
    firmen = models.ManyToManyField('Firma', through='FirmaFahrzeug', blank=True)

    def __str__(self):
        return "{} (Fahrzeuge)".format(self.name)

    @staticmethod
    def get_fields():
        return [
            [{"val": "Name"}],
            [{"val": "Beschreibung"}],
            [{"val": "Ab Stufe"}],
            [{"val": "Schnelligkeit"}],
            [{"val": "Rüstung"}],
            [{"val": "Erfolge"}],
            [{"val": "Günstigster Preis"}],
            [{"val": "Weiteres"}],
            [{"val": "Preis * Stufe?"}]
            ]

    def get_values(self, firma_model=FirmaFahrzeug, url_prefix="shop:buy_fahrzeug"):

        fields = super().get_values(firma_model, url_prefix)
        return fields[:3] +\
            [
                [{"val": self.schnelligkeit}],
                [{"val": self.rüstung}],
                [{"val": self.erfolge}]
            ] + fields[3:]


class Einbauten(BaseShop):
    class Meta:
        verbose_name = "Einbauten"
        verbose_name_plural = "Einbauten"

    manifestverlust = models.CharField(max_length=20, null=True, blank=True)
    kategorie = models.CharField(choices=einbauten_enum, max_length=2, default=einbauten_enum[0][0])
    firmen = models.ManyToManyField('Firma', through='FirmaEinbauten', blank=True)

    def __str__(self):
        return "{} (Einbauten)".format(self.name)

    @staticmethod
    def get_fields():
        return [
            [{"val": "Name"}],
            [{"val": "Beschreibung"}],
            [{"val": "Ab Stufe"}],
            [{"val": "Manifestverlust"}],
            [{"val": "Günstigster Preis"}],
            [{"val": "Weiteres"}],
            [{"val": "Preis * Stufe?"}]
        ]

    def get_values(self, firma_model=FirmaEinbauten, url_prefix="shop:buy_einbauten"):

        fields = super().get_values(firma_model, url_prefix)
        return fields[:3] + [[{"val": self.manifestverlust}]] + fields[3:]


class Zauber(BaseShop):
    class Meta:
        verbose_name = "Zauber"
        verbose_name_plural = "Zauber"

    schaden = models.CharField(max_length=20, default='')
    astralschaden = models.CharField(max_length=20, default='')

    kategorie = models.CharField(choices=zauber_enum, max_length=2, null=True, blank=True)
    flächenzauber = models.BooleanField(default=False)

    firmen = models.ManyToManyField('Firma', through='FirmaZauber', blank=True)

    def __str__(self):
        return "{} (Zauber)".format(self.name)

    @staticmethod
    def get_fields():
        return [
            [{"val": "Name"}],
            [{"val": "Beschreibung"}],
            [{"val": "Ab Stufe"}],
            [{"val": "Schaden"}],
            [{"val": "Astralschaden"}],
            [{"val": "Flächenwirkung"}],
            [{"val": "Günstigster Preis"}],
            [{"val": "Weiteres"}],
            [{"val": "Preis * Stufe?"}]
            ]

    def get_values(self, firma_model=FirmaZauber, url_prefix="shop:buy_zauber"):

        fields = super().get_values(firma_model, url_prefix)
        return fields[:3] +\
            [
                [{"val": self.schaden}],
                [{"val": self.astralschaden}],
                [{"val": "ja" if self.flächenzauber else ""}]
            ] + fields[3:]


class Alchemie(BaseShop):
    class Meta:
        verbose_name = "Alchemie"
        verbose_name_plural = "Alchemie"

    kategorie = models.CharField(choices=alchemie_enum, max_length=2, default=alchemie_enum[0][0])
    firmen = models.ManyToManyField('Firma', through='FirmaAlchemie', blank=True)

    def __str__(self):
        return "{} (Alchemie)".format(self.name)

    def get_values(self, firma_model=FirmaAlchemie, url_prefix="shop:buy_alchemie"):
        return super().get_values(firma_model, url_prefix)


class Tinker(BaseShop):
    class Meta:
        verbose_name = "Für Selbstständige"
        verbose_name_plural = "Für Selbstständige"

    werte = models.TextField(max_length=1500, default='', blank=True)
    kategorie = models.CharField(choices=tinker_enum, max_length=2, default=tinker_enum[0][0])
    firmen = models.ManyToManyField('Firma', through='FirmaTinker', blank=True)

    def __str__(self):
        return "{} (für Selbstständige)".format(self.name)

    @staticmethod
    def get_fields():
        return [
            [{"val": "Name"}],
            [{"val": "Beschreibung"}],
            [{"val": "Ab Stufe"}],
            [{"val": "Werte"}],
            [{"val": "Weiteres"}]
        ]

    def get_values(self, firma_model=FirmaTinker, url_prefix=None):

        weiteres = "illegal" if self.illegal else ""
        if self.lizenz_benötigt and not weiteres:
            weiteres = "Lizenz"
        if self.lizenz_benötigt and self.illegal:
            weiteres += ", Lizenz"

        return [[{"val": self.name, "icon_url": self.getIconUrl(), "name": self.id}],
                [{"val": self.beschreibung}],
                [{"val": self.ab_stufe}],
                [{"val": self.werte}],
                [{"val": weiteres}]
                ]

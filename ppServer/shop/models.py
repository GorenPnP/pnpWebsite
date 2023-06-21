import math

from django.shortcuts import get_object_or_404
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.db.models import Count

from django_resized import ResizedImageField

from . import enums


class ShopCategory(models.Model):
    kategorie = models.CharField(max_length=1, choices=enums.category_enum, null=False, blank=False, default=enums.category_enum[0][0], unique=True)

    def __str__(self):
        return self.get_kategorie_display()


class Modifier(models.Model):

    class Meta:
        ordering = ['prio']
        verbose_name = "Modifier"
        verbose_name_plural = "Modifier"

    prio = models.FloatField(validators=[MinValueValidator(1.0)], default=100, unique=True)

    price_modifier = models.FloatField(null=False, blank=False, default=1.0)
    is_factor_not_addition = models.BooleanField(default=True)
    active = models.BooleanField(default=True)

    firmen = models.ManyToManyField("Firma")
    kategorien = models.ManyToManyField(ShopCategory)

    def __str__(self):
        return "#{} {}{} ({})({})".format(
            self.prio,
            "*" if self.is_factor_not_addition else "+",
            self.price_modifier,
            ", ".join([f.name for f in self.firmen.all()]),
            ", ".join([k.get_kategorie_display() for k in self.kategorien.all()])
        )

    @classmethod
    def getModifier(cls, firma, shopCategory):
        catName = shopCategory._meta.verbose_name_plural
        catEnumValue = ''
        for letter, cat in enums.category_enum:
            if cat == catName:
                catEnumValue = letter
                break

        kategorie = get_object_or_404(ShopCategory, kategorie=catEnumValue) if catEnumValue else None
        specificModifiers =\
            (Modifier.objects.filter(firmen__id__exact=firma.id) if firma else Modifier.objects.none()) |\
            (Modifier.objects.filter(kategorien__id__exact=kategorie.id) if kategorie else Modifier.objects.none())

        baseModifier = Modifier.objects.annotate(Count('firmen')).annotate(Count('kategorien')).filter(firmen__count=0, kategorien__count=0)
        allModifiers = (baseModifier | specificModifiers).filter(active=True).order_by("prio")
        if allModifiers.count() == 0:
            return lambda price: price

        # return function that calculates the modified value of a passed price
        def calcPrice(price: int) -> int:
            for modifier in allModifiers:
                if modifier.is_factor_not_addition:
                    price *= modifier.price_modifier
                else:
                    price += modifier.price_modifier

            return math.floor(price + 0.5)
        return calcPrice
     

# Firma
class Firma(models.Model):
    class Meta:
        ordering = ['name']
        verbose_name = "Firma"
        verbose_name_plural = "Firmen"

    name = models.CharField(max_length=50, default='')
    beschreibung = models.TextField(max_length=1000, default='', blank=True)

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
    preis = models.IntegerField(default=0, null=True)

    verfügbarkeit = models.PositiveIntegerField(default=0)

    def __str__(self):
        return "{} von {} ({}%)".format(self.item, self.firma, self.verfügbarkeit)

    def getPrice(self):
        return Modifier.getModifier(self.firma, self.item.__class__)(self.preis)

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

    def getPriceStufe1(self):
        return Modifier.getModifier(self.firma, self.item.__class__)(self.stufe_1)
    def getPriceStufe2(self):
        return Modifier.getModifier(self.firma, self.item.__class__)(self.stufe_2)
    def getPriceStufe3(self):
        return Modifier.getModifier(self.firma, self.item.__class__)(self.stufe_3)
    def getPriceStufe4(self):
        return Modifier.getModifier(self.firma, self.item.__class__)(self.stufe_4)
    def getPriceStufe5(self):
        return Modifier.getModifier(self.firma, self.item.__class__)(self.stufe_5)

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


class FirmaVergessenerZauber(FirmaShop):
    item = models.ForeignKey('VergessenerZauber', on_delete=models.CASCADE)


class FirmaAlchemie(FirmaShop):
    item = models.ForeignKey('Alchemie', on_delete=models.CASCADE)


class FirmaTinker(FirmaShop):
    item = models.ForeignKey('Tinker', on_delete=models.CASCADE)


class FirmaBegleiter(FirmaShop):
    item = models.ForeignKey('Begleiter', on_delete=models.CASCADE)

class FirmaEngelsroboter(FirmaShop):
    item = models.ForeignKey('Engelsroboter', on_delete=models.CASCADE)

################ Base Shop ####################

class BaseShop(models.Model):
    class Meta:
        abstract = True

    name = models.CharField(max_length=50, default='', unique=True)
    beschreibung = models.TextField(max_length=1500, default='', blank=True)
    icon = ResizedImageField(size=[64, 64], null=True, blank=True)

    ab_stufe = models.IntegerField(default=0, validators=[MinValueValidator(0)], blank=True)
    illegal = models.BooleanField(default=False)
    lizenz_benötigt = models.BooleanField(default=False)

    frei_editierbar = models.BooleanField(default=True)
    stufenabhängig = models.BooleanField(default=False)


    def __str__(self):
        return "{} ({})".format(self.name, self._meta.verbose_name)

    def getIconUrl(self):
        return self.icon.url if self.icon else "/static/res/img/goren_logo.png"


class Item(BaseShop):
    class Meta:
        verbose_name = "Item"
        verbose_name_plural = "Items"

        ordering = ['name']

    kategorie = models.CharField(choices=enums.item_enum, max_length=2, default=enums.item_enum[0][0])
    firmen = models.ManyToManyField('Firma', through='FirmaItem', blank=True, related_name='firmen')


class Waffen_Werkzeuge(BaseShop):
    class Meta:
        verbose_name = "Waffe/Werkzeug"
        verbose_name_plural = "Waffen & Werkzeuge"

        ordering = ['name']

    erfolge = models.PositiveIntegerField(default=0)
    bs = models.CharField(max_length=20, default=0)
    zs = models.CharField(max_length=20, default=0)
    dk = models.PositiveIntegerField(default=0, blank=True, null=True)

    kategorie = models.CharField(choices=enums.werkzeuge_enum, max_length=2, default=enums.werkzeuge_enum[0][0])
    firmen = models.ManyToManyField('Firma', through='FirmaWaffen_Werkzeuge', blank=True)


class Magazin(BaseShop):
    class Meta:
        verbose_name = "Magazin"
        verbose_name_plural = "Magazine"

        ordering = ['name']

    schuss = models.PositiveIntegerField(default=0)
    firmen = models.ManyToManyField('Firma', through='FirmaMagazin', blank=True)


class Pfeil_Bolzen(BaseShop):
    class Meta:
        verbose_name = "Pfeil/Bolzen"
        verbose_name_plural = "Pfeile & Bolzen"

        ordering = ['name']

    bs = models.CharField(max_length=20, default='')
    zs = models.CharField(max_length=20, default='')
    firmen = models.ManyToManyField('Firma', through='FirmaPfeil_Bolzen', blank=True)


class Schusswaffen(BaseShop):
    class Meta:
        verbose_name = "Schusswaffe"
        verbose_name_plural = "Schusswaffen"

        ordering = ['name']

    erfolge = models.PositiveIntegerField(default=0)
    bs = models.CharField(max_length=20, default='')
    zs = models.CharField(max_length=20, default='')

    magazine = models.ManyToManyField(Magazin, blank=True)
    pfeile_bolzen = models.ManyToManyField(Pfeil_Bolzen, blank=True)

    dk = models.PositiveIntegerField(default=0, blank=True)
    präzision = models.PositiveIntegerField(default=0, blank=True)

    kategorie = models.CharField(choices=enums.schusswaffen_enum, max_length=2, default=enums.schusswaffen_enum[0][0])
    firmen = models.ManyToManyField('Firma', through='FirmaSchusswaffen', blank=True)


class Magische_Ausrüstung(BaseShop):
    class Meta:
        verbose_name = "magische Ausrüstung"
        verbose_name_plural = "magische Ausrüstung"

        ordering = ['name']

    kategorie = models.CharField(choices=enums.magische_Ausrüstung_enum, max_length=2, default=enums.magische_Ausrüstung_enum[0][0])
    firmen = models.ManyToManyField('Firma', through='FirmaMagische_Ausrüstung', blank=True)


class Rituale_Runen(BaseShop):
    class Meta:
        verbose_name = "Ritual/Rune"
        verbose_name_plural = "Rituale & Runen"

        ordering = ['name']

    kategorie = models.CharField(choices=enums.rituale_enum, max_length=2, default=enums.rituale_enum[0][0])
    firmen = models.ManyToManyField('Firma', through='FirmaRituale_Runen', blank=True)


class Rüstungen(BaseShop):
    class Meta:
        verbose_name = "Rüstung"
        verbose_name_plural = "Rüstungen"

        ordering = ['name']

    schutz = models.PositiveIntegerField(default=0)
    stärke = models.PositiveIntegerField(default=0)
    haltbarkeit = models.PositiveIntegerField(default=0)

    firmen = models.ManyToManyField('Firma', through='FirmaRüstungen', blank=True)


class Ausrüstung_Technik(BaseShop):
    class Meta:
        verbose_name = "Ausrüstung/Technik"
        verbose_name_plural = "Ausrüstung & Technik"

        ordering = ['name']

    manifestverlust_str = models.CharField(max_length=20, null=True, blank=True)
    manifestverlust = models.DecimalField('manifestverlust', max_digits=4, decimal_places=2,
                                          default=0.0, blank=True, null=True,
                                          validators=[MinValueValidator(0), MaxValueValidator(10)])
    kategorie = models.CharField(choices=enums.ausrüstung_enum, max_length=2, default=enums.ausrüstung_enum[0][0])
    firmen = models.ManyToManyField('Firma', through='FirmaAusrüstung_Technik', blank=True)


class Fahrzeug(BaseShop):
    class Meta:
        verbose_name = "Fahrzeug"
        verbose_name_plural = "Fahrzeuge"

        ordering = ['name']

    schnelligkeit = models.PositiveIntegerField(blank=True, null=True)
    rüstung = models.PositiveIntegerField(blank=True, null=True)
    erfolge = models.PositiveIntegerField(default=0, blank=True, null=True)

    kategorie = models.CharField(choices=enums.fahrzeuge_enum, max_length=2, default=enums.fahrzeuge_enum[0][0])
    firmen = models.ManyToManyField('Firma', through='FirmaFahrzeug', blank=True)


class Einbauten(BaseShop):
    class Meta:
        verbose_name = "Einbauten"
        verbose_name_plural = "Einbauten"

        ordering = ['name']

    manifestverlust = models.CharField(max_length=20, null=True, blank=True)
    kategorie = models.CharField(choices=enums.einbauten_enum, max_length=2, default=enums.einbauten_enum[0][0])
    firmen = models.ManyToManyField('Firma', through='FirmaEinbauten', blank=True)


class Zauber(BaseShop):
    class Meta:
        verbose_name = "Zauber"
        verbose_name_plural = "Zauber"

        ordering = ['name']

    schaden = models.CharField(max_length=100, default='', null=True, blank=True)
    astralschaden = models.CharField(max_length=100, default='', null=True, blank=True)
    manaverbrauch = models.CharField(max_length=100, default='', null=True, blank=True)

    kategorie = models.CharField(choices=enums.zauber_enum, max_length=2, null=True, blank=True)

    firmen = models.ManyToManyField('Firma', through='FirmaZauber', blank=True)


class VergessenerZauber(BaseShop):
    class Meta:
        verbose_name = "vergessener Zauber"
        verbose_name_plural = "vergessene Zauber"

        ordering = ['name']

    schaden = models.CharField(max_length=100, default='', null=True, blank=True)
    astralschaden = models.CharField(max_length=100, default='', null=True, blank=True)
    manaverbrauch = models.CharField(max_length=100, default='', null=True, blank=True)

    firmen = models.ManyToManyField('Firma', through='FirmaVergessenerZauber', blank=True)


class Alchemie(BaseShop):
    class Meta:
        verbose_name = "Alchemie"
        verbose_name_plural = "Alchemie"

        ordering = ['name']

    kategorie = models.CharField(choices=enums.alchemie_enum, max_length=2, default=enums.alchemie_enum[0][0])
    firmen = models.ManyToManyField('Firma', through='FirmaAlchemie', blank=True)


class Tinker(BaseShop):
    class Meta:
        verbose_name = "für Selbstständige"
        verbose_name_plural = "für Selbstständige"

        ordering = ['name']

    werte = models.TextField(max_length=1500, default='', blank=True)
    kategorie = models.CharField(choices=enums.tinker_enum, max_length=2, default=enums.tinker_enum[0][0])
    firmen = models.ManyToManyField('Firma', through='FirmaTinker', blank=True)

    minecraft_mod_id = models.CharField(max_length=512, null=True, blank=True)


    @staticmethod
    def getIdOdMod():
        return "sc"

    def getMinecraftModId(self):
        return self.minecraft_mod_id if ":" in self.minecraft_mod_id else Tinker.getIdOdMod() + ":" + self.minecraft_mod_id

    def toDict(self):
        return {"id": self.id, "name": self.name, "icon_url": self.getIconUrl()}


class Begleiter(BaseShop):
    class Meta:
        verbose_name = "Begleiter"
        verbose_name_plural = "Begleiter"

        ordering = ['name']

    firmen = models.ManyToManyField('Firma', through='FirmaBegleiter', blank=True)


class Engelsroboter(BaseShop):
    class Meta:
        verbose_name = "Engelsroboter"
        verbose_name_plural = "Engelsroboter"

        ordering = ['name']

    ST = models.PositiveSmallIntegerField(default=0, null=False, blank=False, help_text="Stärke")
    UM = models.PositiveSmallIntegerField(default=0, null=False, blank=False, help_text="Umgang")
    MA = models.PositiveSmallIntegerField(default=0, null=False, blank=False, help_text="Magie")
    IN = models.PositiveSmallIntegerField(default=0, null=False, blank=False, help_text="Intelligenz")

    firmen = models.ManyToManyField('Firma', through='FirmaEngelsroboter', blank=True)
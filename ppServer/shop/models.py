from itertools import chain
import math
from PIL import Image as PilImage

from django.shortcuts import get_object_or_404
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.db.models import Count
from django.urls import reverse

from base.models import TableFieldType, TableHeading, TableSerializableModel

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

################ Base Shop ####################

class BaseShop(TableSerializableModel):
    class Meta:
        abstract = True

    name = models.CharField(max_length=50, default='', unique=True)
    beschreibung = models.TextField(max_length=1500, default='', blank=True)
    icon = models.ImageField(null=True, blank=True)

    ab_stufe = models.IntegerField(default=0, validators=[MinValueValidator(0)], blank=True)
    illegal = models.BooleanField(default=False)
    lizenz_benötigt = models.BooleanField(default=False)

    frei_editierbar = models.BooleanField(default=True)
    stufenabhängig = models.BooleanField(default=False)


    @staticmethod
    def get_table_headings():
        return [
            TableHeading("Icon", "icon", TableFieldType.IMAGE),
            TableHeading("Name", "name", TableFieldType.TEXT),
            TableHeading("Beschreibung", "beschreibung", TableFieldType.TEXT),
            TableHeading("Ab Stufe", "ab_stufe", TableFieldType.NUMBER),
            TableHeading("Günstigster Preis", "billigster", TableFieldType.PRICE),
            TableHeading("Weiteres", "weiteres", TableFieldType.TEXT),
            TableHeading("Preis * Stufe?", "stufenabhängig", TableFieldType.BOOLEAN)
        ]

    @classmethod
    def get_all_serialized(cls, url_prefix=None):
        fields = [heading.field for heading in cls.get_table_headings()] + ["pk"]

        objects = cls.objects.filter(frei_editierbar=False)
        if len(objects) == 0: return []

        firma_model = objects[0].firmen.through

        serialized = []

        for object in objects:
            object_dict = object.__dict__

            serialized_object = {}
            for field in fields:
                serialized_object[field] = object_dict[field] if field in object_dict else None

            # add pk
            serialized_object["pk"] = object.pk

            # add "weiteres"
            weiteres = "illegal" if object.illegal else ""
            if object.lizenz_benötigt and not weiteres: weiteres = "Lizenz"
            if object.lizenz_benötigt and object.illegal: weiteres += ", Lizenz"

            serialized_object["weiteres"] = weiteres


            # add "billigster"
            prices = [obj.getPrice() for obj in firma_model.objects.filter(item=object)]
            billigster = sorted(prices)[0] if len(prices) else None
            billigster_preis = billigster if billigster else None
            serialized_object["billigster"] = billigster_preis

            
            # add "icon"
            serialized_object["icon"] = object.getIconUrl()

            # add "url"
            serialized_object["url"] = reverse(url_prefix, args=[object.pk]) if url_prefix else None

            serialized.append(serialized_object)

        return serialized


    def getIconUrl(self):
        return self.icon.url if self.icon else "/static/res/img/icon-dice-account.svg"


    # resize icon
    def save(self, *args, **kwargs):
        MAX_SIZE = 64

        super().save(*args, **kwargs)

        # proceed only if an image exists
        if not self.icon or not self.icon.path: return

        icon = PilImage.open(self.icon.path)

        # is smaller, leave it
        if icon.height <= MAX_SIZE and icon.width <= MAX_SIZE:
            return

        # resize, longest is MAX_SIZE, scale the other accordingly while maintaining ratio
        new_width = MAX_SIZE if icon.width >= icon.height else icon.width * MAX_SIZE // icon.height
        new_height = MAX_SIZE if icon.width <= icon.height else icon.height * MAX_SIZE // icon.width

        icon.thumbnail((new_width, new_height), PilImage.BILINEAR)
        icon.save(self.icon.path)


class Item(BaseShop):
    class Meta:
        verbose_name = "Item"
        verbose_name_plural = "Items"

        ordering = ['name']

    kategorie = models.CharField(choices=enums.item_enum, max_length=2, default=enums.item_enum[0][0])
    firmen = models.ManyToManyField('Firma', through='FirmaItem', blank=True, related_name='firmen')

    def __str__(self):
        return "{} (item)".format(self.name)

    @classmethod
    def get_all_serialized(cls, url_prefix="shop:buy_item"):
        return super().get_all_serialized(url_prefix)


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

    def __str__(self):
        return "{} (Waffen & Werkzeuge)".format(self.name)
    
    @staticmethod
    def get_table_headings():
        return [
            TableHeading("Icon", "icon", TableFieldType.IMAGE),
            TableHeading("Name", "name", TableFieldType.TEXT),
            TableHeading("Beschreibung", "beschreibung", TableFieldType.TEXT),
            TableHeading("Ab Stufe", "ab_stufe", TableFieldType.NUMBER),
            TableHeading("Erfolge", "erfolge", TableFieldType.NUMBER),
            TableHeading("BS", "bs", TableFieldType.TEXT),
            TableHeading("ZS", "zs", TableFieldType.TEXT),
            TableHeading("DK", "dk", TableFieldType.NUMBER),
            TableHeading("Günstigster Preis", "billigster", TableFieldType.PRICE),
            TableHeading("Weiteres", "weiteres", TableFieldType.TEXT),
            TableHeading("Preis * Stufe?", "stufenabhängig", TableFieldType.BOOLEAN)
        ]

    @classmethod
    def get_all_serialized(cls, url_prefix="shop:buy_waffen_werkzeuge"):
        return super().get_all_serialized(url_prefix)


class Magazin(BaseShop):
    class Meta:
        verbose_name = "Magazin"
        verbose_name_plural = "Magazine"

        ordering = ['name']

    schuss = models.PositiveIntegerField(default=0)
    firmen = models.ManyToManyField('Firma', through='FirmaMagazin', blank=True)

    def __str__(self):
        return "{}, {} Schuss (Magazine)".format(self.name, self.schuss)

    @staticmethod
    def get_table_headings():
        return [
            TableHeading("Icon", "icon", TableFieldType.IMAGE),
            TableHeading("Name", "name", TableFieldType.TEXT),
            TableHeading("Beschreibung", "beschreibung", TableFieldType.TEXT),
            TableHeading("Ab Stufe", "ab_stufe", TableFieldType.NUMBER),
            TableHeading("Schuss", "schuss", TableFieldType.NUMBER),
            TableHeading("Günstigster Preis", "billigster", TableFieldType.PRICE),
            TableHeading("Weiteres", "weiteres", TableFieldType.TEXT),
            TableHeading("Preis * Stufe?", "stufenabhängig", TableFieldType.BOOLEAN)
        ]

    @classmethod
    def get_all_serialized(cls, url_prefix="shop:buy_magazine"):
        return super().get_all_serialized(url_prefix)


class Pfeil_Bolzen(BaseShop):
    class Meta:
        verbose_name = "Pfeil/Bolzen"
        verbose_name_plural = "Pfeile & Bolzen"

        ordering = ['name']

    bs = models.CharField(max_length=20, default='')
    zs = models.CharField(max_length=20, default='')
    firmen = models.ManyToManyField('Firma', through='FirmaPfeil_Bolzen', blank=True)

    def __str__(self):
        return "{} (Pfeile & Bolzen)".format(self.name)
    
    @staticmethod
    def get_table_headings():
        return [
            TableHeading("Icon", "icon", TableFieldType.IMAGE),
            TableHeading("Name", "name", TableFieldType.TEXT),
            TableHeading("Beschreibung", "beschreibung", TableFieldType.TEXT),
            TableHeading("Ab Stufe", "ab_stufe", TableFieldType.NUMBER),
            TableHeading("BS", "bs", TableFieldType.TEXT),
            TableHeading("ZS", "zs", TableFieldType.TEXT),
            TableHeading("Günstigster Preis", "billigster", TableFieldType.PRICE),
            TableHeading("Weiteres", "weiteres", TableFieldType.TEXT),
            TableHeading("Preis * Stufe?", "stufenabhängig", TableFieldType.BOOLEAN)
        ]

    @classmethod
    def get_all_serialized(cls, url_prefix="shop:buy_pfeil_bolzen"):
        return super().get_all_serialized(url_prefix)


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

    def __str__(self):
        return "{} (Schusswaffen)".format(self.name)

    @staticmethod
    def get_table_headings():
        return [
            TableHeading("Icon", "icon", TableFieldType.IMAGE),
            TableHeading("Name", "name", TableFieldType.TEXT),
            TableHeading("Beschreibung", "beschreibung", TableFieldType.TEXT),
            TableHeading("Ab Stufe", "ab_stufe", TableFieldType.NUMBER),
            TableHeading("Erfolge", "erfolge", TableFieldType.NUMBER),
            TableHeading("BS", "bs", TableFieldType.TEXT),
            TableHeading("ZS", "zs", TableFieldType.TEXT),
            TableHeading("DK", "dk", TableFieldType.NUMBER),
            TableHeading("Präzision", "präzision", TableFieldType.NUMBER),
            TableHeading("Munition", "munition", TableFieldType.TEXT),
            TableHeading("Günstigster Preis", "billigster", TableFieldType.PRICE),
            TableHeading("Weiteres", "weiteres", TableFieldType.TEXT),
            TableHeading("Preis * Stufe?", "stufenabhängig", TableFieldType.BOOLEAN)
        ]
    
    @classmethod
    def get_all_serialized(cls, url_prefix="shop:buy_schusswaffen"):
        fields = [heading.field for heading in cls.get_table_headings()] + ["pk"]

        objects = cls.objects.filter(frei_editierbar=False)
        if len(objects) == 0: return []

        firma_model = objects[0].firmen.through

        serialized = []

        for object in objects:
            object_dict = object.__dict__

            serialized_object = {}
            for field in fields:
                serialized_object[field] = object_dict[field] if field in object_dict else None

            # add pk
            serialized_object["pk"] = object.pk

            # add "weiteres"
            weiteres = "illegal" if object.illegal else ""
            if object.lizenz_benötigt and not weiteres: weiteres = "Lizenz"
            if object.lizenz_benötigt and object.illegal: weiteres += ", Lizenz"

            serialized_object["weiteres"] = weiteres

            # add "munition"
            serialized_object["munition"] = ", ".join([m.name for m in chain(object.magazine.all(), object.pfeile_bolzen.all())])


            # add "billigster"
            prices = [obj.getPrice() for obj in firma_model.objects.filter(item=object)]
            billigster = sorted(prices)[0] if len(prices) else None
            billigster_preis = billigster if billigster else None
            serialized_object["billigster"] = billigster_preis

            
            # add "icon"
            serialized_object["icon"] = object.getIconUrl()

            # add "url"
            serialized_object["url"] = reverse(url_prefix, args=[object.pk]) if url_prefix else None

            serialized.append(serialized_object)

        return serialized


class Magische_Ausrüstung(BaseShop):
    class Meta:
        verbose_name = "magische Ausrüstung"
        verbose_name_plural = "magische Ausrüstung"

        ordering = ['name']

    kategorie = models.CharField(choices=enums.magische_Ausrüstung_enum, max_length=2, default=enums.magische_Ausrüstung_enum[0][0])
    firmen = models.ManyToManyField('Firma', through='FirmaMagische_Ausrüstung', blank=True)

    def __str__(self):
        return "{} (Magische Ausrüstung)".format(self.name)

    @classmethod
    def get_all_serialized(cls, url_prefix="shop:buy_mag_ausrüstung"):
        return super().get_all_serialized(url_prefix)


class Rituale_Runen(BaseShop):
    class Meta:
        verbose_name = "Ritual/Rune"
        verbose_name_plural = "Rituale & Runen"

        ordering = ['name']

    kategorie = models.CharField(choices=enums.rituale_enum, max_length=2, default=enums.rituale_enum[0][0])
    firmen = models.ManyToManyField('Firma', through='FirmaRituale_Runen', blank=True)

    def __str__(self):
        return "{} (Rituale & Runen)".format(self.name)

    @staticmethod
    def get_table_headings():
        return [
            TableHeading("Icon", "icon", TableFieldType.IMAGE),
            TableHeading("Name", "name", TableFieldType.TEXT),
            TableHeading("Beschreibung", "beschreibung", TableFieldType.TEXT),
            TableHeading("Ab Stufe", "ab_stufe", TableFieldType.NUMBER),
            TableHeading("Stufe 1", "stufe1", TableFieldType.PRICE),
            TableHeading("Stufe 2", "stufe2", TableFieldType.PRICE),
            TableHeading("Stufe 3", "stufe3", TableFieldType.PRICE),
            TableHeading("Stufe 4", "stufe4", TableFieldType.PRICE),
            TableHeading("Stufe 5", "stufe5", TableFieldType.PRICE),
            TableHeading("Weiteres", "weiteres", TableFieldType.TEXT)
        ]
    
    @classmethod
    def get_all_serialized(cls, url_prefix="shop:buy_rituale_runen"):
        fields = [heading.field for heading in cls.get_table_headings()] + ["pk"]

        objects = cls.objects.filter(frei_editierbar=False)
        if len(objects) == 0: return []

        firma_model = objects[0].firmen.through

        serialized = []

        for object in objects:
            object_dict = object.__dict__

            serialized_object = {}
            for field in fields:
                serialized_object[field] = object_dict[field] if field in object_dict else None

            # add pk
            serialized_object["pk"] = object.pk

            # add "weiteres"
            weiteres = "illegal" if object.illegal else ""
            if object.lizenz_benötigt and not weiteres: weiteres = "Lizenz"
            if object.lizenz_benötigt and object.illegal: weiteres += ", Lizenz"

            serialized_object["weiteres"] = weiteres


            # add "billigster"
            if firma_model.objects.filter(item=object).count():
                firma_models = firma_model.objects.filter(item=object)
                serialized_object["stufe1"] = sorted([fm.getPriceStufe1() for fm in firma_models])[0]
                serialized_object["stufe2"] = sorted([fm.getPriceStufe2() for fm in firma_models])[0]
                serialized_object["stufe3"] = sorted([fm.getPriceStufe3() for fm in firma_models])[0]
                serialized_object["stufe4"] = sorted([fm.getPriceStufe4() for fm in firma_models])[0]
                serialized_object["stufe5"] = sorted([fm.getPriceStufe5() for fm in firma_models])[0]

            # add "icon"
            serialized_object["icon"] = object.getIconUrl()

            # add "url"
            serialized_object["url"] = reverse(url_prefix, args=[object.pk]) if url_prefix else None

            serialized.append(serialized_object)

        return serialized


class Rüstungen(BaseShop):
    class Meta:
        verbose_name = "Rüstung"
        verbose_name_plural = "Rüstungen"

        ordering = ['name']

    schutz = models.PositiveIntegerField(default=0)
    stärke = models.PositiveIntegerField(default=0)
    haltbarkeit = models.PositiveIntegerField(default=0)

    firmen = models.ManyToManyField('Firma', through='FirmaRüstungen', blank=True)

    def __str__(self):
        return "{} (Rüstungen)".format(self.name)
    
    @staticmethod
    def get_table_headings():
        return [
            TableHeading("Icon", "icon", TableFieldType.IMAGE),
            TableHeading("Name", "name", TableFieldType.TEXT),
            TableHeading("Beschreibung", "beschreibung", TableFieldType.TEXT),
            TableHeading("Ab Stufe", "ab_stufe", TableFieldType.NUMBER),
            TableHeading("Schutz", "schutz", TableFieldType.NUMBER),
            TableHeading("Stärke", "stärke", TableFieldType.NUMBER),
            TableHeading("Haltbarkeit", "haltbarkeit", TableFieldType.NUMBER),
            TableHeading("Günstigster Preis", "billigster", TableFieldType.PRICE),
            TableHeading("Weiteres", "weiteres", TableFieldType.TEXT),
            TableHeading("Preis * Stufe?", "stufenabhängig", TableFieldType.BOOLEAN)
        ]

    @classmethod
    def get_all_serialized(cls, url_prefix="shop:buy_rüstungen"):
        return super().get_all_serialized(url_prefix)


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

    def __str__(self):
        return "{} (Ausrüstung & Technik)".format(self.name)

    @classmethod
    def get_all_serialized(cls, url_prefix="shop:buy_ausrüstung_technik"):
        return super().get_all_serialized(url_prefix)


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

    def __str__(self):
        return "{} (Fahrzeuge)".format(self.name)
    
    @staticmethod
    def get_table_headings():
        return [
            TableHeading("Icon", "icon", TableFieldType.IMAGE),
            TableHeading("Name", "name", TableFieldType.TEXT),
            TableHeading("Beschreibung", "beschreibung", TableFieldType.TEXT),
            TableHeading("Ab Stufe", "ab_stufe", TableFieldType.NUMBER),
            TableHeading("Schnelligkeit", "schnelligkeit", TableFieldType.NUMBER),
            TableHeading("Rüstung", "rüstung", TableFieldType.NUMBER),
            TableHeading("Erfolge", "erfolge", TableFieldType.NUMBER),
            TableHeading("Günstigster Preis", "billigster", TableFieldType.PRICE),
            TableHeading("Weiteres", "weiteres", TableFieldType.TEXT),
            TableHeading("Preis * Stufe?", "stufenabhängig", TableFieldType.BOOLEAN)
        ]
    
    @classmethod
    def get_all_serialized(cls, url_prefix="shop:buy_fahrzeug"):
        return super().get_all_serialized(url_prefix)


class Einbauten(BaseShop):
    class Meta:
        verbose_name = "Einbauten"
        verbose_name_plural = "Einbauten"

        ordering = ['name']

    manifestverlust = models.CharField(max_length=20, null=True, blank=True)
    kategorie = models.CharField(choices=enums.einbauten_enum, max_length=2, default=enums.einbauten_enum[0][0])
    firmen = models.ManyToManyField('Firma', through='FirmaEinbauten', blank=True)

    def __str__(self):
        return "{} (Einbauten)".format(self.name)

    @staticmethod
    def get_table_headings():
        return [
            TableHeading("Icon", "icon", TableFieldType.IMAGE),
            TableHeading("Name", "name", TableFieldType.TEXT),
            TableHeading("Beschreibung", "beschreibung", TableFieldType.TEXT),
            TableHeading("Ab Stufe", "ab_stufe", TableFieldType.NUMBER),
            TableHeading("Manifestverlust", "manifestverlust", TableFieldType.TEXT),
            TableHeading("Günstigster Preis", "billigster", TableFieldType.PRICE),
            TableHeading("Weiteres", "weiteres", TableFieldType.TEXT),
            TableHeading("Preis * Stufe?", "stufenabhängig", TableFieldType.BOOLEAN)
        ]
    
    @classmethod
    def get_all_serialized(cls, url_prefix="shop:buy_einbauten"):
        return super().get_all_serialized(url_prefix)


class Zauber(BaseShop):
    class Meta:
        verbose_name = "Zauber"
        verbose_name_plural = "Zauber"

        ordering = ['name']

    schaden = models.CharField(max_length=100, default='', null=True, blank=True)
    astralschaden = models.CharField(max_length=100, default='', null=True, blank=True)
    manaverbrauch = models.CharField(max_length=100, default='', null=True, blank=True)

    kategorie = models.CharField(choices=enums.zauber_enum, max_length=2, null=True, blank=True)
    flächenzauber = models.BooleanField(default=False)

    firmen = models.ManyToManyField('Firma', through='FirmaZauber', blank=True)

    def __str__(self):
        return "{} (Zauber)".format(self.name)

    @staticmethod
    def get_table_headings():
        return [
            TableHeading("Icon", "icon", TableFieldType.IMAGE),
            TableHeading("Name", "name", TableFieldType.TEXT),
            TableHeading("Beschreibung", "beschreibung", TableFieldType.TEXT),
            TableHeading("Ab Stufe", "ab_stufe", TableFieldType.NUMBER),
            TableHeading("Schaden", "schaden", TableFieldType.TEXT),
            TableHeading("Astralschaden", "astralschaden", TableFieldType.TEXT),
            TableHeading("Manaverbrauch", "manaverbrauch", TableFieldType.TEXT),
            TableHeading("Flächenwirkung", "flächenzauber", TableFieldType.BOOLEAN),
            TableHeading("Kategorie", "kategorie", TableFieldType.TEXT),
            TableHeading("Günstigster Preis", "billigster", TableFieldType.PRICE),
            TableHeading("Weiteres", "weiteres", TableFieldType.TEXT),
            TableHeading("Preis * Stufe?", "stufenabhängig", TableFieldType.BOOLEAN)
        ]
    
    @classmethod
    def get_all_serialized(cls, url_prefix="shop:buy_zauber"):
        return super().get_all_serialized(url_prefix)


class VergessenerZauber(BaseShop):
    class Meta:
        verbose_name = "vergessener Zauber"
        verbose_name_plural = "vergessene Zauber"

        ordering = ['name']

    schaden = models.CharField(max_length=100, default='', null=True, blank=True)
    astralschaden = models.CharField(max_length=100, default='', null=True, blank=True)
    manaverbrauch = models.CharField(max_length=100, default='', null=True, blank=True)

    flächenzauber = models.BooleanField(default=False)

    firmen = models.ManyToManyField('Firma', through='FirmaVergessenerZauber', blank=True)

    def __str__(self):
        return "{} (vergessener Zauber)".format(self.name)

    @staticmethod
    def get_table_headings():
        return [
            TableHeading("Icon", "icon", TableFieldType.IMAGE),
            TableHeading("Name", "name", TableFieldType.TEXT),
            TableHeading("Beschreibung", "beschreibung", TableFieldType.TEXT),
            TableHeading("Ab Stufe", "ab_stufe", TableFieldType.NUMBER),
            TableHeading("Schaden", "schaden", TableFieldType.TEXT),
            TableHeading("Astralschaden", "astralschaden", TableFieldType.TEXT),
            TableHeading("Manaverbrauch", "manaverbrauch", TableFieldType.TEXT),
            TableHeading("Flächenwirkung", "flächenzauber", TableFieldType.BOOLEAN),
            TableHeading("Günstigster Preis", "billigster", TableFieldType.PRICE),
            TableHeading("Weiteres", "weiteres", TableFieldType.TEXT),
            TableHeading("Preis * Stufe?", "stufenabhängig", TableFieldType.BOOLEAN)
        ]
    
    @classmethod
    def get_all_serialized(cls, url_prefix="shop:buy_vergessener_zauber"):
        return super().get_all_serialized(url_prefix)


class Alchemie(BaseShop):
    class Meta:
        verbose_name = "Alchemie"
        verbose_name_plural = "Alchemie"

        ordering = ['name']

    kategorie = models.CharField(choices=enums.alchemie_enum, max_length=2, default=enums.alchemie_enum[0][0])
    firmen = models.ManyToManyField('Firma', through='FirmaAlchemie', blank=True)

    def __str__(self):
        return "{} (Alchemie)".format(self.name)
    
    @classmethod
    def get_all_serialized(cls, url_prefix="shop:buy_alchemie"):
        return super().get_all_serialized(url_prefix)


class Tinker(BaseShop):
    class Meta:
        verbose_name = "für Selbstständige"
        verbose_name_plural = "für Selbstständige"

        ordering = ['name']

    werte = models.TextField(max_length=1500, default='', blank=True)
    kategorie = models.CharField(choices=enums.tinker_enum, max_length=2, default=enums.tinker_enum[0][0])
    firmen = models.ManyToManyField('Firma', through='FirmaTinker', blank=True)

    def __str__(self):
        return "{} (für Selbstständige)".format(self.name)

    def toDict(self):
        return {"id": self.id, "name": self.name, "icon_url": self.getIconUrl()}

    @staticmethod
    def get_table_headings():
        return [
            TableHeading("Icon", "icon", TableFieldType.IMAGE),
            TableHeading("Name", "name", TableFieldType.TEXT),
            TableHeading("Beschreibung", "beschreibung", TableFieldType.TEXT),
            TableHeading("Ab Stufe", "ab_stufe", TableFieldType.NUMBER),
            TableHeading("Werte", "werte", TableFieldType.TEXT),
            TableHeading("Weiteres", "weiteres", TableFieldType.TEXT),
            TableHeading("Preis * Stufe?", "stufenabhängig", TableFieldType.BOOLEAN)
        ]


class Begleiter(BaseShop):
    class Meta:
        verbose_name = "Begleiter"
        verbose_name_plural = "Begleiter"

        ordering = ['name']

    firmen = models.ManyToManyField('Firma', through='FirmaBegleiter', blank=True)

    def __str__(self):
        return "{} (Begleiter)".format(self.name)
    
    @classmethod
    def get_all_serialized(cls, url_prefix="shop:buy_begleiter"):
        return super().get_all_serialized(url_prefix)
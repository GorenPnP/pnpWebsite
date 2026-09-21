import math

from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.db.models import Count, Q, QuerySet

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
    def getModifier(cls, firma, shopCategory: "BaseShop"):
        # get Category letter of Shop-model
        shopmodel_name = shopCategory._meta.verbose_name_plural
        catLetter = next((letter for letter, cat in enums.category_enum if cat == shopmodel_name), '')

        allModifiers = Modifier.objects\
            .annotate(Count('firmen'), Count('kategorien'))\
            .filter(
                # get category-specific modifiers with correct firma OR category
                Q(firmen=firma) | Q(kategorien__kategorie=catLetter) |
                # get base modifiers (that modify everything)
                Q(firmen__count=0, kategorien__count=0)
            )\
            .filter(active=True).order_by("prio")
        
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


############################################

class Tag(models.Model):
    class Meta:
        ordering = ['name']
        verbose_name = "Tag"
        verbose_name_plural = "Tags"

    icon = ResizedImageField(size=[64, 64], null=True, blank=True)
    name = models.CharField(max_length=32, unique=True)

    def __str__(self):
        return self.name

class Slot(models.Model):
    class Meta:
        abstract = True
        ordering = ['item', 'tag']
        verbose_name = "Slot"
        verbose_name_plural = "Slots"

    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)
    num = models.PositiveSmallIntegerField(validators=[MinValueValidator(1)], default=1)

    class PreloadManager(models.Manager):
        def get_queryset(self) -> QuerySet:
            """ adds 'tag' field """
            return super().get_queryset().prefetch_related("tag", "item")
    objects = PreloadManager()

    def __str__(self):
        return f'{self.item} hat {self.num}x {self.tag.name} Slots'


class SlotNahkampfwaffe(Slot):
    item = models.ForeignKey("Nahkampfwaffe", on_delete=models.CASCADE)

class SlotFernkampfwaffe(Slot):
    item = models.ForeignKey("Fernkampfwaffe", on_delete=models.CASCADE)

class SlotRitual_Rune(Slot):
    item = models.ForeignKey("Ritual_Rune", on_delete=models.CASCADE)

class SlotEinbaute(Slot):
    item = models.ForeignKey("Einbaute", on_delete=models.CASCADE)

class SlotZauber(Slot):
    item = models.ForeignKey("Zauber", on_delete=models.CASCADE)

class SlotBegleiter(Slot):
    item = models.ForeignKey("Begleiter", on_delete=models.CASCADE)


class Upgrade(models.Model):

    class Meta:
        ordering = ['tag', 'name', 'ab_stufe', 'price']
        verbose_name = "Upgrade"
        verbose_name_plural = "Upgrades"

    fields_enum = [
        ('schaden', 'Schaden'),
        ('schadensart', 'Schadensart'),
        ('dk', 'DK'),
        ('schuss', 'Schuss'),
        ('präzision', 'Präzision'),
        ('reichweite', 'Reichweite'),
        ('wirkbereich', 'Wirkbereich'),
        ('händigkeit', 'Händigkeit'),
        ('feuerrate', 'Feuerrate'),
        ('manaverbrauch', 'Manaverbrauch'),
        # ('manifestverlust', 'Manifestverlust'),
        ('hp', 'HP'),
        ('physische_reaktion', 'physische Reaktion'),
        ('astrale_reaktion', 'astrale Reaktion'),
        ('physischer_widerstand', 'physischer Widerstand'),
        ('astraler_widerstand', 'astraler Widerstand'),
    ]

    # properties
    name = models.CharField(max_length=32)
    beschreibung = models.TextField(default='', blank=True)
    tag = models.ForeignKey(Tag, on_delete=models.SET_NULL, null=True)

    # requirements to get
    ab_stufe = models.PositiveSmallIntegerField(default=0)
    price = models.IntegerField(default=0)
    achievement_unlock = models.BooleanField(default=False, verbose_name="nur manuell von SL nach Achievement freischaltbar")

    # calc
    influenced_field = models.CharField(max_length=64, choices=fields_enum, null=True, blank=True)
    field_value = models.TextField(default='', blank=True)

    class PreloadTagManager(models.Manager):
        def get_queryset(self) -> QuerySet:
            """ adds 'tag' field """
            return super().get_queryset().prefetch_related("tag")
    objects = PreloadTagManager()

    def __str__(self):
        return "{} #{}".format(self.name, self.tag.name)



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


class FirmaNahkampfwaffe(FirmaShop):
    item = models.ForeignKey('Nahkampfwaffe', on_delete=models.CASCADE)


class FirmaMunition(FirmaShop):
    item = models.ForeignKey('Munition', on_delete=models.CASCADE)


class FirmaFernkampfwaffe(FirmaShop):
    item = models.ForeignKey('Fernkampfwaffe', on_delete=models.CASCADE)


class FirmaMagische_Ausrüstung(FirmaShop):
    item = models.ForeignKey('Magische_Ausrüstung', on_delete=models.CASCADE)


class FirmaRitual_Rune(FirmaShop):
    item = models.ForeignKey('Ritual_Rune', on_delete=models.CASCADE)


class FirmaRüstung(FirmaShop):
    item = models.ForeignKey('Rüstung', on_delete=models.CASCADE)


class FirmaAusrüstung_Technik(FirmaShop):
    item = models.ForeignKey('Ausrüstung_Technik', on_delete=models.CASCADE)


class FirmaFahrzeug(FirmaShop):
    item = models.ForeignKey('Fahrzeug', on_delete=models.CASCADE)


class FirmaEinbaute(FirmaShop):
    item = models.ForeignKey('Einbaute', on_delete=models.CASCADE)


class FirmaZauber(FirmaShop):
    item = models.ForeignKey('Zauber', on_delete=models.CASCADE)


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

    frei_editierbar = models.BooleanField(default=True)
    stufenabhängig = models.BooleanField(default=False)
    has_implementation = models.BooleanField(default=False, verbose_name="ist implementiert")


    def __str__(self):
        return "{} ({})".format(self.name, self._meta.verbose_name)

    def getIconUrl(self):
        return self.icon.url if self.icon else "/static/res/img/goren_logo.png"
    
    def cheapest(self, stufe=1) -> int or None:
        offers = getattr(self, f"{self.firmen.through._meta.model_name}_set").all()
        if not offers: return None

        return sorted([o.getPrice() for o in offers])[0] * stufe

    @staticmethod
    def getShopDisplayFields():
        return [
            "name", "beschreibung", "icon", "ab_stufe", "preis",    # preis needs to be added separately by firmen->preis/stufe_1
        ]


class Item(BaseShop):
    class Meta:
        verbose_name = "Item"
        verbose_name_plural = "Items"

        ordering = ['name']

    kategorie = models.CharField(choices=enums.item_enum, max_length=2, default=enums.item_enum[0][0])
    firmen = models.ManyToManyField('Firma', through='FirmaItem', blank=True, related_name='firmen')

    @staticmethod
    def getShopDisplayFields():
        return super(Item, Item).getShopDisplayFields() + ["kategorie"]


class Nahkampfwaffe(BaseShop):
    class Meta:
        verbose_name = "Nahkampf-/Wurfwaffe"
        verbose_name_plural = "Nahkampf-/Wurfwaffen"

        ordering = ['name']

    bs = models.CharField(max_length=20, default=0)
    zs = models.CharField(max_length=20, default=0)
    schaden = models.CharField(max_length=64, default=0)
    dk = models.PositiveIntegerField(default=0, blank=True, null=True)
    schadensart = models.CharField(max_length=1, choices=enums.schadensart_enum, null=True, blank=True)

    reichweite = models.FloatField(default=0.0, verbose_name="Reichweite in m")
    wirkbereich = models.TextField(default='', blank=True)
    händigkeit = models.CharField(max_length=1, choices=enums.hand_enum, default='1')
    fertigkeit = models.ForeignKey('character.Fertigkeit', on_delete=models.SET_NULL, null=True, blank=True)

    slots = models.ManyToManyField(Tag, through=SlotNahkampfwaffe)
    possible_upgrades = models.ManyToManyField(Upgrade)

    kategorie = models.CharField(choices=enums.nahkampfwaffe_enum, max_length=2, default=enums.nahkampfwaffe_enum[0][0])
    firmen = models.ManyToManyField('Firma', through='FirmaNahkampfwaffe', blank=True)

    @staticmethod
    def getShopDisplayFields():
        return super(Nahkampfwaffe, Nahkampfwaffe).getShopDisplayFields() + ["bs", "zs", "dk", "schadensart", "fertigkeit", "kategorie"]


class Munition(BaseShop):
    class Meta:
        verbose_name = "Munition"
        verbose_name_plural = "Munition"

        ordering = ['name']

    bs = models.CharField(max_length=20, default='')
    zs = models.CharField(max_length=20, default='')
    schaden = models.CharField(max_length=64, default=0)
    schadensart = models.CharField(max_length=1, choices=enums.schadensart_enum, null=True, blank=True)
    wirkbereich = models.TextField(default='', blank=True)

    firmen = models.ManyToManyField('Firma', through='FirmaMunition', blank=True)

    def __str__(self):
        return f"{self.name} ({self.schaden if self.schaden and self.schaden != '0' else f'{self.bs}|{self.zs}'} {self.get_schadensart_display()})"

    @staticmethod
    def getShopDisplayFields():
        return super(Munition, Munition).getShopDisplayFields() + ['bs', 'zs', 'schadensart', 'wirkbereich']


class Fernkampfwaffe(BaseShop):
    class Meta:
        verbose_name = "Fernkampfwaffe"
        verbose_name_plural = "Fernkampfwaffen"

        ordering = ['name']

    schuss = models.PositiveIntegerField(default=1)
    dk = models.PositiveIntegerField(default=0, blank=True)
    präzision = models.PositiveIntegerField(default=0, blank=True)
    feuerrate = models.CharField(max_length=1, choices=enums.feuerrate_enum, default=enums.feuerrate_enum[2][0])
    reichweite = models.FloatField(default=0.0, verbose_name="Reichweite in m")
    wirkbereich = models.TextField(default='', blank=True)
    händigkeit = models.CharField(max_length=1, choices=enums.hand_enum, default='1')

    munition = models.ManyToManyField(Munition, blank=True)

    slots = models.ManyToManyField(Tag, through=SlotFernkampfwaffe)
    possible_upgrades = models.ManyToManyField(Upgrade)

    fertigkeit = models.ForeignKey('character.Fertigkeit', on_delete=models.SET_NULL, null=True, blank=True)
    kategorie = models.CharField(choices=enums.fernkampfwaffe_enum, max_length=1, default=enums.fernkampfwaffe_enum[0][0])
    firmen = models.ManyToManyField('Firma', through='FirmaFernkampfwaffe', blank=True)

    @staticmethod
    def getShopDisplayFields():
        return super(Fernkampfwaffe, Fernkampfwaffe).getShopDisplayFields() + ["fertigkeit", "dk", "präzision", "kategorie", "munition"]


class Magische_Ausrüstung(BaseShop):
    class Meta:
        verbose_name = "magische Ausrüstung"
        verbose_name_plural = "magische Ausrüstung"

        ordering = ['name']

    kategorie = models.CharField(choices=enums.magische_Ausrüstung_enum, max_length=2, default=enums.magische_Ausrüstung_enum[0][0])
    firmen = models.ManyToManyField('Firma', through='FirmaMagische_Ausrüstung', blank=True)

    @staticmethod
    def getShopDisplayFields():
        return super(Magische_Ausrüstung, Magische_Ausrüstung).getShopDisplayFields() + ["kategorie"]

class Ritual_Rune(BaseShop):
    class Meta:
        verbose_name = "Ritual/Rune"
        verbose_name_plural = "Rituale/Runen"

        ordering = ['name']

    schaden = models.CharField(max_length=64, default=0)
    schadensart = models.CharField(max_length=1, choices=enums.schadensart_enum, null=True, blank=True)
    wirkbereich = models.TextField(default='', blank=True)

    manaverbrauch = models.CharField(max_length=100, default='', null=True, blank=True)

    slots = models.ManyToManyField(Tag, through=SlotRitual_Rune)
    possible_upgrades = models.ManyToManyField(Upgrade)

    kategorie = models.CharField(choices=enums.ritual_enum, max_length=2, default=enums.ritual_enum[0][0])
    firmen = models.ManyToManyField('Firma', through='FirmaRitual_Rune', blank=True)

    @staticmethod
    def getShopDisplayFields():
        return super(Ritual_Rune, Ritual_Rune).getShopDisplayFields() + ["kategorie"]


class Rüstung(BaseShop):
    class Meta:
        verbose_name = "Rüstung"
        verbose_name_plural = "Rüstungen"

        ordering = ['name']

    schutz = models.CharField(default="0", max_length=64)
    haltbarkeit = models.PositiveIntegerField(default=0)
    damage_speciality = models.TextField(default='', verbose_name="Besonderheiten bei Schadensarten")

    kategorie = models.CharField(choices=enums.ruestung_enum, max_length=2, default=enums.ruestung_enum[0][0])
    firmen = models.ManyToManyField('Firma', through='FirmaRüstung', blank=True)

    @staticmethod
    def getShopDisplayFields():
        return super(Rüstung, Rüstung).getShopDisplayFields() + ["schutz", "haltbarkeit"]


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

    @staticmethod
    def getShopDisplayFields():
        return super(Ausrüstung_Technik, Ausrüstung_Technik).getShopDisplayFields() + ["manifestverlust", "manifestverlust_str", "kategorie"]

class Fahrzeug(BaseShop):
    class Meta:
        verbose_name = "Fahrzeug"
        verbose_name_plural = "Fahrzeuge"

        ordering = ['name']

    geschwindigkeit = models.PositiveIntegerField(blank=True, null=True)
    hp = models.PositiveIntegerField(blank=True, null=True)
    erfolge = models.PositiveIntegerField(default=0, blank=True, null=True)

    kategorie = models.CharField(choices=enums.fahrzeuge_enum, max_length=2, default=enums.fahrzeuge_enum[0][0])
    firmen = models.ManyToManyField('Firma', through='FirmaFahrzeug', blank=True)

    @staticmethod
    def getShopDisplayFields():
        return super(Fahrzeug, Fahrzeug).getShopDisplayFields() + ["geschwindigkeit", "hp", "erfolge", "kategorie"]


class Einbaute(BaseShop):
    class Meta:
        verbose_name = "Einbaute"
        verbose_name_plural = "Einbauten"

        ordering = ['name']

    manifestverlust = models.CharField(max_length=20, null=True, blank=True)

    slots = models.ManyToManyField(Tag, through=SlotEinbaute)
    possible_upgrades = models.ManyToManyField(Upgrade)

    kategorie = models.CharField(choices=enums.einbaute_enum, max_length=2, default=enums.einbaute_enum[0][0])
    firmen = models.ManyToManyField('Firma', through='FirmaEinbaute', blank=True)

    @staticmethod
    def getShopDisplayFields():
        return super(Einbaute, Einbaute).getShopDisplayFields() + ["manifestverlust", "kategorie"]


class Zauber(BaseShop):
    class Meta:
        verbose_name = "Zauber"
        verbose_name_plural = "Zauber"

        ordering = ['name']

    astralschaden = models.CharField(max_length=100, default='', null=True, blank=True)
    manaverbrauch = models.CharField(max_length=100, default='', null=True, blank=True)
    verteidigung = models.CharField(max_length=1, choices=enums.zauberverteidigung_enum, default=enums.zauberverteidigung_enum[0][0], verbose_name="Reaktion")

    schaden = models.CharField(max_length=64, default=0)
    schadensart = models.CharField(max_length=1, choices=enums.schadensart_enum, null=True, blank=True)
    wirkbereich = models.TextField(default='', blank=True)
    wirkdauer = models.TextField(default='', blank=True)

    slots = models.ManyToManyField(Tag, through=SlotZauber)
    possible_upgrades = models.ManyToManyField(Upgrade)

    kategorie = models.CharField(choices=enums.zauber_enum, max_length=2, null=True, blank=True)
    firmen = models.ManyToManyField('Firma', through='FirmaZauber', blank=True)

    @staticmethod
    def getShopDisplayFields():
        return super(Zauber, Zauber).getShopDisplayFields() + ["astralschaden", "manaverbrauch", "verteidigung", "schadensart", "kategorie"]


class Alchemie(BaseShop):
    class Meta:
        verbose_name = "Alchemie"
        verbose_name_plural = "Alchemie"

        ordering = ['name']

    kategorie = models.CharField(choices=enums.alchemie_enum, max_length=2, default=enums.alchemie_enum[0][0])
    firmen = models.ManyToManyField('Firma', through='FirmaAlchemie', blank=True)

    @staticmethod
    def getShopDisplayFields():
        return super(Alchemie, Alchemie).getShopDisplayFields() + ["kategorie"]


class Tinker(BaseShop):
    class Meta:
        verbose_name = "für Selbstständige"
        verbose_name_plural = "für Selbstständige"

        ordering = ['name']

    werte = models.TextField(max_length=1500, default='', blank=True)
    kategorie = models.CharField(choices=enums.tinker_enum, max_length=2, default=enums.tinker_enum[0][0])
    firmen = models.ManyToManyField('Firma', through='FirmaTinker', blank=True)

    minecraft_mod_id = models.CharField(max_length=512, null=True, blank=True)
    wooble_buy_price = models.FloatField(default=1.0)
    wooble_sell_price = models.FloatField(default=1.0)

    @staticmethod
    def getShopDisplayFields():
        return super(Tinker, Tinker).getShopDisplayFields() + ["werte", "kategorie"]

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

    hp = models.CharField(max_length=64, default='')
    physische_reaktion = models.CharField(max_length=64, default='')
    astrale_reaktion = models.CharField(max_length=64, default='')
    astraler_widerstand = models.CharField(max_length=64, default='')
    physischer_widerstand = models.CharField(max_length=64, default='')

    slots = models.ManyToManyField(Tag, through=SlotBegleiter)
    possible_upgrades = models.ManyToManyField(Upgrade)

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

    hp = models.CharField(max_length=64, default='')
    physische_reaktion = models.CharField(max_length=64, default='')
    astrale_reaktion = models.CharField(max_length=64, default='')
    astraler_widerstand = models.CharField(max_length=64, default='')
    physischer_widerstand = models.CharField(max_length=64, default='')

    firmen = models.ManyToManyField('Firma', through='FirmaEngelsroboter', blank=True)

    @staticmethod
    def getShopDisplayFields():
        return super(Engelsroboter, Engelsroboter).getShopDisplayFields() + ["ST", "UM", "MA", "IN"]

from datetime import date

from django.core.validators import MaxValueValidator
from django.db import models

from shop.models import *


############ RelShop ###########

class RelShop(models.Model):
    class Meta:
        abstract = True
        ordering = ['char', 'item']
        unique_together = (('char', 'item', "notizen"),)

    char = models.ForeignKey("character.Charakter", on_delete=models.CASCADE)
    anz = models.PositiveIntegerField(default=1)
    stufe = models.PositiveIntegerField(default=None, null=True, blank=True)
    notizen = models.CharField(max_length=50, blank=True, default='')

    def __str__(self):
        return "{} ({})".format(self.item, self.anz)


class RelItem(RelShop):
    class Meta:
        verbose_name = "Item"
        verbose_name_plural = "Items"

    item = models.ForeignKey(Item, on_delete=models.CASCADE)


class RelNahkampfwaffe(RelShop):
    class Meta:
        verbose_name = "Nahkampf-/Wurfwaffe"
        verbose_name_plural = "Nahkampf-/Wurfwaffen"

    item = models.ForeignKey(Nahkampfwaffe, on_delete=models.CASCADE)


class RelMunition(RelShop):
    class Meta:
        verbose_name = "Munition"
        verbose_name_plural = "Munition"

    item = models.ForeignKey(Munition, on_delete=models.CASCADE)


class RelFernkampfwaffe(RelShop):
    class Meta:
        verbose_name = "Fernkampfwaffe"
        verbose_name_plural = "Fernkampfwaffen"

    item = models.ForeignKey(Fernkampfwaffe, on_delete=models.CASCADE)


class RelMagische_Ausrüstung(RelShop):
    class Meta:
        verbose_name = "magische Ausrüstung"
        verbose_name_plural = "magische Ausrüstung"

    item = models.ForeignKey(Magische_Ausrüstung, on_delete=models.CASCADE)


class RelRüstung(RelShop):
    class Meta:
        verbose_name = "Rüstung"
        verbose_name_plural = "Rüstungen"

    item = models.ForeignKey(Rüstung, on_delete=models.CASCADE)


class RelTechnik(RelShop):
    class Meta:
        verbose_name = "Technik"
        verbose_name_plural = "Technik"

    item = models.ForeignKey(Technik, on_delete=models.CASCADE)
    selbst_eingebaut = models.BooleanField(default=False)


class RelFahrzeug(RelShop):
    class Meta:
        verbose_name = "Fahrzeug"
        verbose_name_plural = "Fahrzeuge"

    item = models.ForeignKey(Fahrzeug, on_delete=models.CASCADE)


class RelEinbaute(RelShop):
    class Meta:
        verbose_name = "Einbaute"
        verbose_name_plural = "Einbauten"

    item = models.ForeignKey(Einbaute, on_delete=models.CASCADE)


class RelZauber(RelShop):
    class Meta:
        verbose_name = "Zauber"
        verbose_name_plural = "Zauber"

    item = models.ForeignKey(Zauber, on_delete=models.CASCADE)
    tier = models.PositiveSmallIntegerField(default=0, validators=[MaxValueValidator(7)])

    learned = models.BooleanField(default=False)

    def __str__(self):
        return "{}".format(self.item)


class RelAlchemie(RelShop):
    class Meta:
        verbose_name = "Alchemie"
        verbose_name_plural = "Alchemie"

    item = models.ForeignKey(Alchemie, on_delete=models.CASCADE)


class RelTinker(RelShop):
    class Meta:
        verbose_name = "Für Selbstständige"
        verbose_name_plural = "Für Selbstständige"

    item = models.ForeignKey(Tinker, on_delete=models.CASCADE)


class RelBegleiter(RelShop):
    class Meta:
        verbose_name = "Begleiter"
        verbose_name_plural = "Begleiter"

    item = models.ForeignKey(Begleiter, on_delete=models.CASCADE, null=True)


class RelEngelsroboter(RelShop):
    class Meta:
        verbose_name = "Engelsroboter"
        verbose_name_plural = "Engelsroboter"

    item = models.ForeignKey(Engelsroboter, on_delete=models.CASCADE, null=True)


class RelRitual_Rune(RelShop):
    class Meta:
        verbose_name = "Ritual/Rune"
        verbose_name_plural = "Rituale/Runen"

    item = models.ForeignKey(Ritual_Rune, on_delete=models.CASCADE)


############ RelShopAvailable ###########
class RelShopAvailable(models.Model):
    class Meta:
        abstract = True
        ordering = ['char', 'item']
        unique_together = (('char', "item"),)

    char = models.ForeignKey("character.Charakter", on_delete=models.CASCADE)
    last_tried = models.DateField(default=date.today)

    def __str__(self):
        return "{}, {}, {}".format(self.item, self.char, self.last_tried)


class RelItemAvailable(RelShopAvailable):
    class Meta:
        verbose_name = "Item Verfügbarkeit"
        verbose_name_plural = "Items Verfügbarkeiten"

    item = models.ForeignKey(Item, on_delete=models.CASCADE)


class RelNahkampfwaffeAvailable(RelShopAvailable):
    class Meta:
        verbose_name = "Nahkampf-/Wurfwaffe Verfügbarkeit"
        verbose_name_plural = "Nahkampf-/Wurfwaffe Verfügbarkeiten"

    item = models.ForeignKey(Nahkampfwaffe, on_delete=models.CASCADE)


class RelMunitionAvailable(RelShopAvailable):
    class Meta:
        verbose_name = "Munition Verfügbarkeit"
        verbose_name_plural = "Munition Verfügbarkeiten"

    item = models.ForeignKey(Munition, on_delete=models.CASCADE)


class RelFernkampfwaffeAvailable(RelShopAvailable):
    class Meta:
        verbose_name = "Fernkampfwaffe Verfügbarkeit"
        verbose_name_plural = "Fernkampfwaffen Verfügbarkeiten"

    item = models.ForeignKey(Fernkampfwaffe, on_delete=models.CASCADE)


class RelMagische_AusrüstungAvailable(RelShopAvailable):
    class Meta:
        verbose_name = "magische Ausrüstung Verfügbarkeit"
        verbose_name_plural = "magische Ausrüstung Verfügbarkeiten"

    item = models.ForeignKey(Magische_Ausrüstung, on_delete=models.CASCADE)


class RelRüstungAvailable(RelShopAvailable):
    class Meta:
        verbose_name = "Rüstung Verfügbarkeit"
        verbose_name_plural = "Rüstungen Verfügbarkeiten"

    item = models.ForeignKey(Rüstung, on_delete=models.CASCADE)


class RelTechnikAvailable(RelShopAvailable):
    class Meta:
        verbose_name = "Technik Verfügbarkeit"
        verbose_name_plural = "Technik Verfügbarkeiten"

    item = models.ForeignKey(Technik, on_delete=models.CASCADE)


class RelFahrzeugAvailable(RelShopAvailable):
    class Meta:
        verbose_name = "Fahrzeug Verfügbarkeit"
        verbose_name_plural = "Fahrzeuge Verfügbarkeiten"

    item = models.ForeignKey(Fahrzeug, on_delete=models.CASCADE)


class RelEinbauteAvailable(RelShopAvailable):
    class Meta:
        verbose_name = "Einbaute Verfügbarkeit"
        verbose_name_plural = "Einbaute Verfügbarkeiten"

    item = models.ForeignKey(Einbaute, on_delete=models.CASCADE)


class RelZauberAvailable(RelShopAvailable):
    class Meta:
        verbose_name = "Zauber Verfügbarkeit"
        verbose_name_plural = "Zauber Verfügbarkeiten"

    item = models.ForeignKey(Zauber, on_delete=models.CASCADE)

    def __str__(self):
        return "{}".format(self.item)


class RelAlchemieAvailable(RelShopAvailable):
    class Meta:
        verbose_name = "Alchemie Verfügbarkeit"
        verbose_name_plural = "Alchemie Verfügbarkeiten"

    item = models.ForeignKey(Alchemie, on_delete=models.CASCADE)


class RelTinkerAvailable(RelShopAvailable):
    class Meta:
        verbose_name = "Für Selbstständige Verfügbarkeit"
        verbose_name_plural = "Für Selbstständige Verfügbarkeiten"

    item = models.ForeignKey(Tinker, on_delete=models.CASCADE)


class RelBegleiterAvailable(RelShopAvailable):
    class Meta:
        verbose_name = "Begleiter Verfügbarkeit"
        verbose_name_plural = "Begleiter Verfügbarkeiten"

    item = models.ForeignKey(Begleiter, on_delete=models.CASCADE)


class RelEngelsroboterAvailable(RelShopAvailable):
    class Meta:
        verbose_name = "Engelsroboter Verfügbarkeit"
        verbose_name_plural = "Engelsroboter Verfügbarkeiten"

    item = models.ForeignKey(Engelsroboter, on_delete=models.CASCADE)


class RelRitual_RuneAvailable(RelShopAvailable):
    class Meta:
        verbose_name = "Ritual/Rune Verfügbarkeit"
        verbose_name_plural = "Ritual/Rune Verfügbarkeiten"

    item = models.ForeignKey(Ritual_Rune, on_delete=models.CASCADE)


# Addition

class RelRamsch(RelShop):
    class Meta:
        verbose_name = "Ramsch"
        verbose_name_plural = "Ramsch"

    item = models.CharField(max_length=128, blank=False)

from datetime import date

from django.apps import apps
from django.core.validators import MaxValueValidator
from django.db import models
from django.forms import ValidationError

from shop.models import *


############ RelShop ###########

class RelShop(models.Model):
    class Meta:
        abstract = True
        ordering = ['char', 'item']

    char = models.ForeignKey("character.Charakter", on_delete=models.CASCADE)
    stufe = models.PositiveIntegerField(default=None, null=True, blank=True)
    notizen = models.CharField(max_length=50, blank=True, default='')

    def __str__(self):
        return self.item.__str__()


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


############### UpgradeSlot ###################

class UpgradeSlot(models.Model):
    class Meta:
        abstract = True
        unique_together = ["upgrade", "relitem"]

    upgrade = models.ForeignKey(Upgrade, on_delete=models.CASCADE)

    class PreloadManager(models.Manager):
        def get_queryset(self) -> QuerySet:
            """ adds some fields """
            return super().get_queryset().select_related("upgrade__tag", "slot__item", "relitem__char", "relitem__item").prefetch_related("slot__tag")
    objects = PreloadManager()

    def __str__(self):
        return f"{self.upgrade} in Slot#{'|'.join(self.slot.tag.values_list("name", flat=True))} an {self.slot.item} von {self.relitem.char}"

    def check_custom_m2m_constraints(self):
        item = self.slot.item
        char = self.relitem.char

        print("CHECK UpgradeSlot..", self)

        # num Upgrades has to be lte to available Slots
        if self.slot.num < self.relitem.upgradeslot_set.filter(slot=self.slot).count():
            raise ValidationError("Zu viele Upgrades für die Slots")

        # Slot-Info contains (num, tag, item). RelShop.item has to be the same.
        if self.relitem.item != self.slot.item or not self.slot.tag.filter(pk=self.upgrade.tag.pk).exists():
            raise ValidationError("Slot-Information passt nicht zum item")

        # Upgrade has to be available
        RelUpgrade = apps.get_model("character", f"relupgrade{item._meta.model_name}")
        relUpgrade = RelUpgrade.objects.filter(char=char, item=item).first()
        choosable_upgrades = relUpgrade.get_choosable_Upgrades() if relUpgrade else item.possible_upgrades.filter(achievement_unlock=False)
        if  not choosable_upgrades.filter(pk=self.upgrade.pk).exists():
            raise ValidationError("Upgrade ist nicht freigeschaltet")


class UpgradeSlotNahkampfwaffe(UpgradeSlot):
    slot = models.ForeignKey(SlotNahkampfwaffe, on_delete=models.CASCADE)
    relitem = models.ForeignKey(RelNahkampfwaffe, on_delete=models.CASCADE, related_name="upgradeslot_set")

class UpgradeSlotFernkampfwaffe(UpgradeSlot):
    slot = models.ForeignKey(SlotFernkampfwaffe, on_delete=models.CASCADE)
    relitem = models.ForeignKey(RelFernkampfwaffe, on_delete=models.CASCADE, related_name="upgradeslot_set")

class UpgradeSlotRitual_Rune(UpgradeSlot):
    slot = models.ForeignKey(SlotRitual_Rune, on_delete=models.CASCADE)
    relitem = models.ForeignKey(RelRitual_Rune, on_delete=models.CASCADE, related_name="upgradeslot_set")

class UpgradeSlotRüstung(UpgradeSlot):
    slot = models.ForeignKey(SlotRüstung, on_delete=models.CASCADE)
    relitem = models.ForeignKey(RelRüstung, on_delete=models.CASCADE, related_name="upgradeslot_set")

class UpgradeSlotEinbaute(UpgradeSlot):
    slot = models.ForeignKey(SlotEinbaute, on_delete=models.CASCADE)
    relitem = models.ForeignKey(RelEinbaute, on_delete=models.CASCADE, related_name="upgradeslot_set")

class UpgradeSlotZauber(UpgradeSlot):
    slot = models.ForeignKey(SlotZauber, on_delete=models.CASCADE)
    relitem = models.ForeignKey(RelZauber, on_delete=models.CASCADE, related_name="upgradeslot_set")

class UpgradeSlotBegleiter(UpgradeSlot):
    slot = models.ForeignKey(SlotBegleiter, on_delete=models.CASCADE)
    relitem = models.ForeignKey(RelBegleiter, on_delete=models.CASCADE, related_name="upgradeslot_set")


############### RelUpgrade ###################

class RelUpgrade(models.Model):
    class Meta:
        abstract = True

        ordering = ["char", "item", "points"]
        unique_together = ["char", "item"]

    char = models.ForeignKey("character.Charakter", on_delete=models.CASCADE)

    points = models.PositiveSmallIntegerField(default=0, blank=True)
    unlocked_upgrades = models.ManyToManyField(Upgrade, blank=True)

    class PreloadManager(models.Manager):
        def get_queryset(self) -> QuerySet:
            """ adds some fields """
            return super().get_queryset().select_related("char__eigentümer__user").prefetch_related("item__possible_upgrades__tag", "unlocked_upgrades__tag", "own_upgrades__upgrade__tag")
    objects = PreloadManager()

    def __str__(self):
        return f"{self.char} {self.item} {self.points} Punkt/e"


    def check_custom_m2m_constraints(self) -> None:
        '''
        Needs to be used by ModelForms for RelUpgrade as follows:

        def clean(self):
            res = super().clean()

            # check if the custom constraints are met by calling instance.check_custom_m2m_constraints().
            # We attempt to save the instance and related fields here AND reverse it with atomic & an arbitrary error (AssertionError one line down).
            # Raised ValidationErrors are NOT cached.
            # from BaseForm.clean(): "Any ValidationError raised by this method will not be associated with a particular field;
            # it will have a special-case association with the field named '__all__'"
            try:
                with transaction.atomic():
                    self.instance.save()
                    self._save_m2m()
                    self.instance.check_custom_m2m_constraints()
                    raise AssertionError()
            except AssertionError:
                return res
        
        '''
        print("CHECK CONSTRAINTS", self)

        # unlocked_upgrades need to be possible for the item
        if self.unlocked_upgrades.exclude(pk__in=self.item.possible_upgrades.all()).exists():
            raise ValidationError("Freigeschaltete Upgrades müssen für das Item möglich sein")
        
        # unlocked_upgrades need to be unlockable
        if self.unlocked_upgrades.filter(achievement_unlock=False).exists():
            raise ValidationError("Freigeschaltete Upgrades müssen freischaltbar sein")


        # NOTE: out of OwnUpgrade
        for own_upgrade in self.own_upgrades.select_related("upgrade").all():

            # upgrade is not suited for item
            if not self.item.possible_upgrades.filter(pk=own_upgrade.upgrade.pk).exists():
                raise ValidationError("Upgrade muss zum Item passen")

            # ab_stufe of upgrade is grater than chars ep_stufe
            if own_upgrade.upgrade.ab_stufe > self.char.ep_stufe:
                raise ValidationError("Upgrade benötigt höhere Stufe")

            # unlockable upgrade needs to be unlocked first
            if own_upgrade.upgrade.achievement_unlock and not self.unlocked_upgrades.filter(pk=own_upgrade.upgrade).exists():
                raise ValidationError("Upgrade muss erst freigeschaltet sein")

            # prerequisite of Upgrade is met
            if not self.get_choosable_Upgrades().filter(pk=own_upgrade.upgrade.pk).exists():
                raise ValidationError("Upgrade ist nicht wählbar")

    def get_choosable_Upgrades(self) -> QuerySet[Upgrade]:
        shop_name = self.item._meta.model_name  # name of the type[BaseShop] model of the related item

        # owned upgrades attached to items
        used_upgrades = (Q(**{f"upgradeslot{shop_name}__relitem__item": self.item}) & Q(**{f"upgradeslot{shop_name}__relitem__char": self.char}))
        own_upgrades = (Q(**{f"ownupgrade{shop_name}__relUpgrade": self}))
        unlocked_upgrades = (Q(**{f"relupgrade{shop_name}__item": self.item}) & Q(**{f"relupgrade{shop_name}__char": self.char}))
        without_prerequisites = (Q(pk__in=self.item.possible_upgrades.filter(Q(prerequisite=None))))
        with_prerequisites = (Q(prerequisite__in=Upgrade.objects.filter(used_upgrades | own_upgrades)))

        return Upgrade.objects.filter(
            used_upgrades | own_upgrades | unlocked_upgrades | without_prerequisites | with_prerequisites
        ).filter(ab_stufe__lte=self.char.ep_stufe)


class RelUpgradeNahkampfwaffe(RelUpgrade):
    item = models.ForeignKey(Nahkampfwaffe, on_delete=models.CASCADE)

class RelUpgradeFernkampfwaffe(RelUpgrade):
    item = models.ForeignKey(Fernkampfwaffe, on_delete=models.CASCADE)

class RelUpgradeRitual_Rune(RelUpgrade):
    item = models.ForeignKey(Ritual_Rune, on_delete=models.CASCADE)

class RelUpgradeRüstung(RelUpgrade):
    item = models.ForeignKey(Rüstung, on_delete=models.CASCADE)

class RelUpgradeEinbaute(RelUpgrade):
    item = models.ForeignKey(Einbaute, on_delete=models.CASCADE)

class RelUpgradeZauber(RelUpgrade):
    item = models.ForeignKey(Zauber, on_delete=models.CASCADE)

class RelUpgradeBegleiter(RelUpgrade):
    item = models.ForeignKey(Begleiter, on_delete=models.CASCADE)


############### OwnUpgrade ###################

class OwnUpgrade(models.Model):
    class Meta:
        abstract=True
        ordering = ["upgrade", "num"]

    num = models.PositiveSmallIntegerField(default=1, validators=[MinValueValidator(1)], blank=True)
    upgrade = models.ForeignKey(Upgrade, on_delete=models.CASCADE)

    class PreloadManager(models.Manager):
        def get_queryset(self) -> QuerySet:
            """ adds some fields """
            return super().get_queryset().prefetch_related("relUpgrade__char__eigentümer__user", "relUpgrade__item__possible_upgrades__tag", "relUpgrade__unlocked_upgrades__tag", "upgrade__tag")
    objects = PreloadManager()

    def __str__(self):
        return f"{self.num}x {self.upgrade}"

    def check_custom_m2m_constraints(self) -> None:
        return self.relUpgrade.check_custom_m2m_constraints()

class OwnUpgradeNahkampfwaffe(OwnUpgrade):
    relUpgrade = models.ForeignKey(RelUpgradeNahkampfwaffe, on_delete=models.CASCADE, related_name="own_upgrades")

class OwnUpgradeFernkampfwaffe(OwnUpgrade):
    relUpgrade = models.ForeignKey(RelUpgradeFernkampfwaffe, on_delete=models.CASCADE, related_name="own_upgrades")

class OwnUpgradeRitual_Rune(OwnUpgrade):
    relUpgrade = models.ForeignKey(RelUpgradeRitual_Rune, on_delete=models.CASCADE, related_name="own_upgrades")

class OwnUpgradeRüstung(OwnUpgrade):
    relUpgrade = models.ForeignKey(RelUpgradeRüstung, on_delete=models.CASCADE, related_name="own_upgrades")

class OwnUpgradeEinbaute(OwnUpgrade):
    relUpgrade = models.ForeignKey(RelUpgradeEinbaute, on_delete=models.CASCADE, related_name="own_upgrades")

class OwnUpgradeZauber(OwnUpgrade):
    relUpgrade = models.ForeignKey(RelUpgradeZauber, on_delete=models.CASCADE, related_name="own_upgrades")

class OwnUpgradeBegleiter(OwnUpgrade):
    relUpgrade = models.ForeignKey(RelUpgradeBegleiter, on_delete=models.CASCADE, related_name="own_upgrades")

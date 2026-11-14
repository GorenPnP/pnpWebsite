import math

from django.db import models
from django.db.models import QuerySet
from django.forms import ValidationError

from cards.models import Transaction
from character.models.rel import RelAttribut, RelFertigkeit

from .enums import target_fieldname_enum

class Effect(models.Model):
    class Meta:
        verbose_name = "Effekt"
        verbose_name_plural = "Effekte"
        ordering = ['target_fieldname']

    wertaenderung = models.DecimalField(decimal_places=2, max_digits=15, null=True, blank=True, verbose_name="Wertänderung")
    wertaenderung_str = models.CharField(max_length=32, null=True, blank=True, verbose_name="Wertänderung (str)")
    target_fieldname = models.CharField(choices=target_fieldname_enum)


    target_attribut = models.ForeignKey("character.Attribut", on_delete=models.SET_DEFAULT, default=None, null=True, blank=True)
    target_fertigkeit = models.ForeignKey("character.Fertigkeit", on_delete=models.SET_DEFAULT, default=None, null=True, blank=True)

    source_vorteil = models.ForeignKey("character.Vorteil", on_delete=models.CASCADE, null=True, blank=True)
    source_nachteil = models.ForeignKey("character.Nachteil", on_delete=models.CASCADE, null=True, blank=True)
    source_talent = models.ForeignKey("character.Talent", on_delete=models.CASCADE, null=True, blank=True)
    source_gfsAbility = models.ForeignKey("character.GfsAbility", on_delete=models.CASCADE, null=True, blank=True)
    source_klasse = models.ForeignKey("character.Klasse", on_delete=models.CASCADE, null=True, blank=True)
    source_klasseAbility = models.ForeignKey("character.KlasseAbility", on_delete=models.CASCADE, null=True, blank=True)

    source_shopBegleiter = models.ForeignKey("shop.Begleiter", on_delete=models.CASCADE, null=True, blank=True)
    source_shopMagischeAusrüstung = models.ForeignKey("shop.Magische_Ausrüstung", on_delete=models.CASCADE, null=True, blank=True)
    source_shopRüstung = models.ForeignKey("shop.Rüstung", on_delete=models.CASCADE, null=True, blank=True)
    source_shopEinbaute = models.ForeignKey("shop.Einbaute", on_delete=models.CASCADE, null=True, blank=True)

    has_custom_implementation = models.BooleanField(default=False, null=False, blank=False)

    @property
    def wert(self) -> str or Decimal:
        return self.wertaenderung_str or self.wertaenderung

    @property
    def source(self) -> str:
        return ', '.join([getattr(self, field.replace('_id', '')).__str__() for field, val in self.__dict__.items() if 'source_' in field and val])


    def __str__(self):

        addition = ""
        if "character.RelAttribut" in self.target_fieldname and getattr(self, "target_attribut", None):
            addition = self.target_attribut.__str__()
        elif "character.RelFertigkeit" in self.target_fieldname and getattr(self, "target_fertigkeit", None):
            addition = self.target_fertigkeit.__str__()

        return f"{self.wert} {self.get_target_fieldname_display()}{' (' + addition + ')' if addition else ''}"


    def clean(self) -> None:
        super().clean()


        # source models

        fieldnames = [field for field, val in self.__dict__.items() if "source_" in field and val]
        if len(fieldnames) != 1:
            raise ValidationError("Gebe genau EINE source dieses Effekts an")
        
        old_instance = self.pk and Effect.objects.get(pk=self.pk)
        if old_instance and self.source != old_instance.source:
            raise ValidationError("Die Source darf nach der Erstellung nicht verändert werden")


        # target models

        if "character.RelAttribut" in self.target_fieldname:
            if not getattr(self, "target_attribut", None):
                raise ValidationError("Attribut nicht ausgewählt")
            if getattr(self, "target_fertigkeit", None):
                raise ValidationError("Fertigkeit unnötigerweise ausgewählt")

        elif "character.RelFertigkeit" in self.target_fieldname:
            if not getattr(self, "target_fertigkeit", None):
                raise ValidationError("Fertigkeit nicht ausgewählt")
            if getattr(self, "target_attribut", None):
                raise ValidationError("Attribut unnötigerweise ausgewählt")

        elif ("character.Charakter" in self.target_fieldname or "cards.Card" in self.target_fieldname) and (getattr(self, "target_attribut", None) or getattr(self, "target_fertigkeit", None)):
            raise ValidationError("Attribut oder Fertigkeit unnötigerweise ausgewählt")
        
        if self.target_fieldname in ["character.Charakter.physischer_widerstand_bonus_str", "character.Charakter.astraler_widerstand_bonus_str"]:
            if self.wertaenderung:
                raise ValidationError("wertänderung unnötigerweise ausgewählt bei string-Feld")
        else:
            if self.wertaenderung_str:
                raise ValidationError("wertänderung_str unnötigerweise ausgewählt bei number-Feld")


class RelEffect(models.Model):
    class Meta:
        verbose_name = "Charakter-Effekt"
        verbose_name_plural = "Charakter-Effekte"
        ordering = ['effect']
        unique_together = ["target_char", "effect", "target_attribut"]

    effect = models.ForeignKey(Effect, on_delete=models.CASCADE, null=False)
    target_char = models.ForeignKey("character.Charakter", on_delete=models.CASCADE, null=False, blank=False)

    target_attribut = models.ForeignKey("character.RelAttribut", on_delete=models.SET_DEFAULT, default=None, null=True, blank=True)
    wertaenderung = models.DecimalField(decimal_places=2, max_digits=15, null=True, blank=True, verbose_name="Wertänderung bei custom implementations")
    wertaenderung_str = models.CharField(max_length=32, null=True, blank=True, verbose_name="Wertänderung (str) bei custom implementations")

    is_active = models.BooleanField(default=True, null=False, blank=False, verbose_name="ist aktiv")

    class PreloadEffectManager(models.Manager):
        def get_queryset(self) -> QuerySet:
            """ adds 'user' field """
            return super().get_queryset().select_related("effect", "target_char__eigentümer__user", "target_attribut__attribut")
    objects = PreloadEffectManager()

    @property
    def wert(self) -> str or Decimal:
        if self.effect.target_fieldname.endswith("_str"):
            return self.wertaenderung_str if self.wertaenderung_str is not None else self.effect.wertaenderung_str
        return self.wertaenderung if self.wertaenderung is not None else self.effect.wertaenderung

    def __str__(self):
        return f"{self.effect.__str__()} - {self.target_char}"

    def clean(self) -> None:
        super().clean()

        self.effect.clean()

        # target RelModel has to have a relation to self.target_char

        attr = getattr(self, "target_attribut", None)
        if attr and attr.char != self.target_char:
            raise ValidationError("Attribut vom falschen Charakter")

        if not self.effect.has_custom_implementation:
            if getattr(self, "target_attribut", None):
                raise ValidationError("Attribut gesetzt, aber wird nicht benötigt")

            if getattr(self, "wertaenderung", None):
                raise ValidationError("Wertänderung gesetzt, aber wird nicht benötigt")
            if getattr(self, "wertaenderung_str", None):
                raise ValidationError("Wertänderung_str gesetzt, aber wird nicht benötigt")

        else:
            if "character.RelAttribut" in self.effect.target_fieldname and not getattr(self, "target_attribut", None):
                raise ValidationError("Attribut nicht gesetzt, aber wird benötigt")

            if self.effect.target_fieldname.endswith("_str") and self.wertaenderung is not None:
                return ValidationError("Wertänderung gesetzt, aber es ist ein string-Feld")
            if not self.effect.target_fieldname.endswith("_str") and self.wertaenderung_str:
                return ValidationError("Wertänderung_str gesetzt, aber es ist ein Zahlenfeld")


    def activate(self, save=True):
        [Model, field] = self.effect.target_fieldname.rsplit(".", 1)

        wert = self.wert
        source = self.effect.source

        # get target object
        if Model == "character.RelAttribut":
            target = getattr(self, "target_attribut", RelAttribut.objects.get(char=self.target_char, attribut=self.effect.target_attribut))
        elif Model == "character.RelFertigkeit":
            target = RelFertigkeit.objects.get(char=self.target_char, fertigkeit=self.effect.target_fertigkeit)
        elif Model == "cards.Card":
            target = getattr(self, "target_char").card
        else:
            target = getattr(self, "target_char")

        # set change
        if self.effect.target_fieldname == "character.Charakter. Konto":
            diff = wert - target.card.money
            target.card.money = wert
            target.card.save(update_fields=["money"])

            if diff:
                Transaction.objects.create(
                    sender=target.card if diff < 0 else None,
                    receiver=target.card if diff >= 0 else None,
                    amount=math.fabs(diff),
                    reason=f"Aktiver Effekt von {source} setzt das Konto auf {wert:n} Dr.",
                )

        elif self.effect.target_fieldname.rsplit("_", 1)[-1] == "fix":
            setattr(target, field, wert)
            target.save(update_fields=[field])
        elif self.effect.target_fieldname in ["character.Charakter.physischer_widerstand_bonus_str", "character.Charakter.astraler_widerstand_bonus_str"]:
            setattr(target, field, f'{getattr(target, field)} + {wert}' if getattr(target, field, False) else wert)
            target.save(update_fields=[field])
        else:
            setattr(target, field, (getattr(target, field, 0) or 0) + wert)

            # add notiz to "sonstiger_manifestverlust"
            if self.effect.target_fieldname == "character.Charakter.sonstiger_manifestverlust":
                setattr(target, "notizen_sonstiger_manifestverlust", ", ".join([s for s in [getattr(target, "notizen_sonstiger_manifestverlust", ""), source] if s]))
                target.save(update_fields=[field, "notizen_sonstiger_manifestverlust"])
            else:
                target.save(update_fields=[field])

        # additional 'logging' for money transaction
        if self.effect.target_fieldname == "cards.Card.money" and wert:
            Transaction.objects.create(
                sender=target if wert < 0 else None,
                receiver=target if wert >= 0 else None,
                amount=math.fabs(wert),
                reason=f"Aktiver Effekt von {source}",
            )

        # set is_active (& save)
        self.is_active = True
        if save:
            self.save(update_fields=["is_active"])

        # trigger .signals.apply_hp_effect_of_haustierfels()
        if self.effect.target_fieldname == "character.Charakter.HPplus_fix": self.target_char.save(update_fields=["HPplus_fix"])


    def deactivate(self, save=True):
        [Model, field] = self.effect.target_fieldname.rsplit(".", 1)

        wert = self.wert
        source = self.effect.source

        # get target object
        if Model == "character.RelAttribut":
            target = getattr(self, "target_attribut", RelAttribut.objects.get(char=self.target_char, attribut=self.effect.target_attribut))
        elif Model == "character.RelFertigkeit":
            target = RelFertigkeit.objects.get(char=self.target_char, fertigkeit=self.effect.target_fertigkeit)
        elif Model == "cards.Card":
            target = getattr(self, "target_char").card
        else:
            target = getattr(self, "target_char")

        # set change
        if self.effect.target_fieldname == "character.Charakter. Konto":
            diff = -1 * target.card.money
            target.card.money = 0
            target.card.save(update_fields=["money"])

            if diff:
                Transaction.objects.create(
                    sender=target.card if diff < 0 else None,
                    receiver=target.card if diff >= 0 else None,
                    amount=math.fabs(diff),
                    reason=f"Deaktivieren des Effekts von {source} setzt das Konto auf 0 Dr.",
                )

        elif self.effect.target_fieldname.rsplit("_", 1)[-1] == "fix":
            setattr(target, field, None)
            target.save(update_fields=[field])
        elif self.effect.target_fieldname in ["character.Charakter.physischer_widerstand_bonus_str", "character.Charakter.astraler_widerstand_bonus_str"]:
            parts = (getattr(target, field, "") or "").split(" + ")
            parts.remove(wert)
            setattr(target, field, " + ".join(parts))
            target.save(update_fields=[field])
        else:
            setattr(target, field, (getattr(target, field, 0) or 0) - wert)

            # rm notiz of "sonstiger_manifestverlust"
            if self.effect.target_fieldname == "character.Charakter.sonstiger_manifestverlust":
                setattr(target, "notizen_sonstiger_manifestverlust", ", ".join([s for s in getattr(target, "notizen_sonstiger_manifestverlust", "").split(", ") if s and s != source]))
                target.save(update_fields=[field, "notizen_sonstiger_manifestverlust"])
            else:
                target.save(update_fields=[field])

        # additional 'logging' for money transaction
        if self.effect.target_fieldname == "cards.Card.money" and wert:
            Transaction.objects.create(
                sender=target if wert > 0 else None,
                receiver=target if wert <= 0 else None,
                amount=math.fabs(wert),
                reason=f"Deaktivieren des Effekts von {source}",
            )

        # set is_active (& save)
        self.is_active = False
        if save:
            self.save(update_fields=["is_active"])

        # trigger .signals.apply_hp_effect_of_haustierfels()
        if self.effect.target_fieldname == "character.Charakter.HPplus_fix": self.target_char.save(update_fields=["HPplus_fix"])
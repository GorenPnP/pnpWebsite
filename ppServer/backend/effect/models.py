import math

from django.db import models
from django.forms import ValidationError

from cards.models import Transaction


class AbstractEffect(models.Model):
    class Meta:
        abstract = True

  
    target_fieldname_enum = [
        ("character.RelAttribut.aktuellerWert", "Attribut: Wert"),
        ("character.RelAttribut.aktuellerWert_fix", "Attribut: Wert fix"),
        ("character.RelAttribut.aktuellerWert_bonus", "Attribut: Bonus"),
        ("character.RelAttribut.maxWert", "Attribut: Maximum"),
        ("character.RelAttribut.maxWert_fix", "Attribut: Maximum fix"),

        ("character.RelFertigkeit.fp", "Fertigkeit: FP"),
        ("character.RelFertigkeit.fp_bonus", "Fertigkeit: Bonus"),

        ("character.Charakter.ap", "Charakter: AP"),
        ("character.Charakter.ip", "Charakter: IP"),
        ("character.Charakter.fp", "Charakter: FP"),
        ("character.Charakter.fg", "Charakter: FG"),
        ("character.Charakter.tp", "Charakter: TP"),
        ("character.Charakter.sp", "Charakter: SP"),
        ("character.Charakter.sp_fix", "Charakter: SP fix"),

        ("cards.Card.money", "Charakter: Geld"),
        ("character.Charakter. Konto", "Charakter: neuer Kontostand (-> Geld)"),
        ("character.Charakter.prestige", "Charakter: Prestige"),
        ("character.Charakter.verzehr", "Charakter: Verzehr"),
        ("character.Charakter.sanität", "Charakter: Sanität"),
        ("character.Charakter.glück", "Charakter: Glück"),
        ("character.Charakter.sonstiger_manifestverlust", "Charakter: Manifestverlust"),
        ("character.Charakter.manifest_fix", "Charakter: Manifest fix"),

        ("character.Charakter.speed_laufen_bonus", "Charakter: Bewegung Laufen Bonus"),
        ("character.Charakter.speed_schwimmen_bonus", "Charakter: Bewegung Schwimmen Bonus"),
        ("character.Charakter.speed_fliegen_bonus", "Charakter: Bewegung Fliegen Bonus"),
        ("character.Charakter.speed_astral_bonus", "Charakter: Bewegung Astral Bonus"),

        ("character.Charakter.HPplus", "Charakter: kHP plus"),
        ("character.Charakter.HPplus_fix", "Charakter: kHP plus fix"),
        ("character.Charakter.HPplus_geistig", "Charakter: gHP plus"),
        ("character.Charakter.rang", "Charakter: Rang"),

        ("character.Charakter.crit_attack", "Charakter: Crit-Angriff"),
        ("character.Charakter.crit_defense", "Charakter: Crit-Verteidigung"),
        ("character.Charakter.wesenschaden_waff_kampf", "Charakter: Schaden waffenloser Kampf"),
        ("character.Charakter.wesenschaden_andere_gestalt", "Charakter: Schaden waffenloser Kampf (andere Form)"),

        ("character.Charakter.konzentration", "Charakter: Konzentration"),
        ("character.Charakter.konzentration_fix", "Charakter: Konzentration fix"),
        ("character.Charakter.initiative_bonus", "Charakter: Initiative-Bonus"),
        ("character.Charakter.reaktion_bonus", "Charakter: Reaktionsbonus"),
        ("character.Charakter.natürlicher_schadenswiderstand_bonus", "Charakter: nat. SchaWi-Bonus"),
        ("character.Charakter.natürlicher_schadenswiderstand_bonus_str", "Charakter: nat. SchaWi-Bonus Text"),
        ("character.Charakter.astralwiderstand_bonus", "Charakter: AsWi-Bonus"),
        ("character.Charakter.astralwiderstand_bonus_str", "Charakter: AsWi-Bonus Text"),
        ("character.Charakter.manaoverflow_bonus", "Charakter: Manaoverflow-Bonus"),
        ("character.Charakter.nat_regeneration_bonus", "Charakter: nat. Regeneration-Bonus"),
        ("character.Charakter.immunsystem_bonus", "Charakter: Immunsystem-Bonus"),
    ]

    wertaenderung = models.DecimalField(decimal_places=2, max_digits=15, null=False, blank=True, verbose_name="Wertänderung")
    wertaenderung_str = models.CharField(max_length=32, null=False, blank=True, verbose_name="Wertänderung (str)")
    target_fieldname = models.CharField(choices=target_fieldname_enum)


    def __str__(self):

        addition = ""
        if "character.RelAttribut" in self.target_fieldname and getattr(self, "target_attribut", None):
            addition = self.target_attribut.__str__()
        elif "character.RelFertigkeit" in self.target_fieldname and getattr(self, "target_fertigkeit", None):
            addition = self.target_fertigkeit.__str__()

        return f"{self.wertaenderung_str or self.wertaenderung} {self.get_target_fieldname_display()}{' (' + addition + ')' if addition else ''}"


    def clean(self) -> None:
        super().clean()


        # source models

        fieldnames = [field for field, val in self.__dict__.items() if "source_" in field and val]
        if len(fieldnames) != 1:
            raise ValidationError("Gebe genau EINE source dieses Effekts an")


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
        
        if self.target_fieldname in ["character.Charakter.natürlicher_schadenswiderstand_bonus_str", "character.Charakter.astralwiderstand_bonus_str"]:
            if self.wertaenderung:
                raise ValidationError("wertänderung unnötigerweise ausgewählt bei string-Feld")
        else:
            if self.wertaenderung_str:
                raise ValidationError("wertänderung_str unnötigerweise ausgewählt bei number-Feld")




class Effect(AbstractEffect):
    class Meta:
        verbose_name = "Effekt"
        verbose_name_plural = "Effekte"
        ordering = ['target_fieldname']

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
    source_shopAusrüstungTechnik = models.ForeignKey("shop.Ausrüstung_Technik", on_delete=models.CASCADE, null=True, blank=True)
    source_shopEinbauten = models.ForeignKey("shop.Einbauten", on_delete=models.CASCADE, null=True, blank=True)

    has_custom_implementation = models.BooleanField(default=False, null=False, blank=False)


class RelEffect(AbstractEffect):
    class Meta:
        verbose_name = "Charakter-Effekt"
        verbose_name_plural = "Charakter-Effekte"
        ordering = ['target_fieldname']

    target_char = models.ForeignKey("character.Charakter", on_delete=models.CASCADE, null=False, blank=False)
    target_attribut = models.ForeignKey("character.RelAttribut", on_delete=models.SET_DEFAULT, default=None, null=True, blank=True)
    target_fertigkeit = models.ForeignKey("character.RelFertigkeit", on_delete=models.SET_DEFAULT, default=None, null=True, blank=True)

    source_vorteil = models.ForeignKey("character.RelVorteil", on_delete=models.CASCADE, null=True, blank=True)
    source_nachteil = models.ForeignKey("character.RelNachteil", on_delete=models.CASCADE, null=True, blank=True)
    source_talent = models.ForeignKey("character.RelTalent", on_delete=models.CASCADE, null=True, blank=True)
    source_gfsAbility = models.ForeignKey("character.RelGfsAbility", on_delete=models.CASCADE, null=True, blank=True)
    source_klasse = models.ForeignKey("character.RelKlasse", on_delete=models.CASCADE, null=True, blank=True)
    source_klasseAbility = models.ForeignKey("character.RelKlasseAbility", on_delete=models.CASCADE, null=True, blank=True)

    source_shopBegleiter = models.ForeignKey("character.RelBegleiter", on_delete=models.CASCADE, null=True, blank=True)
    source_shopMagischeAusrüstung = models.ForeignKey("character.RelMagische_Ausrüstung", on_delete=models.CASCADE, null=True, blank=True)
    source_shopRüstung = models.ForeignKey("character.RelRüstung", on_delete=models.CASCADE, null=True, blank=True)
    source_shopAusrüstungTechnik = models.ForeignKey("character.RelAusrüstung_Technik", on_delete=models.CASCADE, null=True, blank=True)
    source_shopEinbauten = models.ForeignKey("character.RelEinbauten", on_delete=models.CASCADE, null=True, blank=True)

    is_active = models.BooleanField(default=True, null=False, blank=False)

    def clean(self) -> None:
        super().clean()

        # source RelModel has to have a relation to self.target_char

        fieldnames = [field.replace("_id", "") for field, val in self.__dict__.items() if "source_" in field and val]
        wrong_relations = [fieldname for fieldname in fieldnames if getattr(self, fieldname).char != self.target_char]
        if wrong_relations:
            raise ValidationError(f"Folgende Felder gehören nicht zum 'target_char': {', '.join(wrong_relations)}")



        # target RelModel has to have a relation to self.target_char

        attr = getattr(self, "target_attribut", None)
        if attr and attr.char != self.target_char:
                raise ValidationError("Attribut vom falschen Charakter")

        fert = getattr(self, "target_fertigkeit", None)
        if fert and fert.char != self.target_char:
                raise ValidationError("Fertigkeit vom falschen Charakter")
    

    def activate(self, save=True):
        [Model, field] = self.target_fieldname.rsplit(".", 1)

        # get target object
        if Model == "character.RelAttribut":
            target = getattr(self, "target_attribut")
        elif Model == "character.RelFertigkeit":
            target = getattr(self, "target_fertigkeit")
        elif Model == "cards.Card":
            target = getattr(self, "target_char").card
        else:
            target = getattr(self, "target_char")

        # set change
        if self.target_fieldname == "character.Charakter. Konto":
            diff = self.wertaenderung - target.card.money
            target.card.money = self.wertaenderung
            target.card.save(update_fields=["money"])

            Transaction.objects.create(
                sender=target.card if diff < 0 else None,
                receiver=target.card if diff >= 0 else None,
                amount=math.fabs(diff),
                reason=f"Aktiver Effekt von {', '.join([getattr(self, field.replace('_id', '')).__str__() for field, val in self.__dict__.items() if 'source_' in field and val])} setzt das Konto auf {self.wertaenderung:n} Dr.",
            )

        elif self.target_fieldname.rsplit("_", 1)[-1] == "fix":
            setattr(target, field, self.wertaenderung)
            target.save(update_fields=[field])
        elif self.target_fieldname in ["character.Charakter.natürlicher_schadenswiderstand_bonus_str", "character.Charakter.astralwiderstand_bonus_str"]:
            target[field] = f'{target[field]} + {self.wertaenderung_str}' if target[field] else self.wertaenderung_str
            target.save(update_fields=[field])
        else:
            setattr(target, field, (getattr(target, field, 0) or 0) + self.wertaenderung)

            # add notiz to "sonstiger_manifestverlust"
            if self.target_fieldname == "character.Charakter.sonstiger_manifestverlust":
                source = [getattr(self, field.replace("_id", "")).__str__() for field, val in self.__dict__.items() if "source_" in field and val][0]
                setattr(target, "notizen_sonstiger_manifestverlust", ", ".join([s for s in [getattr(target, "notizen_sonstiger_manifestverlust", ""), source] if s]))
                target.save(update_fields=[field, "notizen_sonstiger_manifestverlust"])
            else:
                target.save(update_fields=[field])

        # additional 'logging' for money transaction
        if self.target_fieldname == "cards.Card.money":
            Transaction.objects.create(
                sender=target if self.wertaenderung < 0 else None,
                receiver=target if self.wertaenderung >= 0 else None,
                amount=math.fabs(self.wertaenderung),
                reason=f"Aktiver Effekt von {', '.join([getattr(self, field.replace('_id', '')).__str__() for field, val in self.__dict__.items() if 'source_' in field and val])}",
            )

        # set is_active (& save)
        self.is_active = True
        if save:
            self.save(update_fields=["is_active"])


    def deactivate(self, save=True):
        [Model, field] = self.target_fieldname.rsplit(".", 1)

        # get target object
        if Model == "character.RelAttribut":
            target = getattr(self, "target_attribut")
        elif Model == "character.RelFertigkeit":
            target = getattr(self, "target_fertigkeit")
        elif Model == "cards.Card":
            target = getattr(self, "target_char").card
        else:
            target = getattr(self, "target_char")

        # set change
        if self.target_fieldname == "character.Charakter. Konto":
            diff = -1 * target.card.money
            target.card.money = 0
            target.card.save(update_fields=["money"])

            Transaction.objects.create(
                sender=target.card if diff < 0 else None,
                receiver=target.card if diff >= 0 else None,
                amount=math.fabs(diff),
                reason=f"Deaktivieren des Effekts von {', '.join([getattr(self, field.replace('_id', '')).__str__() for field, val in self.__dict__.items() if 'source_' in field and val])} setzt das Konto auf 0 Dr.",
            )

        elif self.target_fieldname.rsplit("_", 1)[-1] == "fix":
            setattr(target, field, None)
            target.save(update_fields=[field])
        elif self.target_fieldname in ["character.Charakter.natürlicher_schadenswiderstand_bonus_str", "character.Charakter.astralwiderstand_bonus_str"]:
            parts = (target[field] or "").split(" + ").remove(self.wertaenderung_str)
            target[field] = " + ".join(parts)
            target.save(update_fields=[field])
        else:
            setattr(target, field, (getattr(target, field, 0) or 0) - self.wertaenderung)

            # rm notiz of "sonstiger_manifestverlust"
            if self.target_fieldname == "character.Charakter.sonstiger_manifestverlust":
                source = [getattr(self, field.replace("_id", "")).__str__() for field, val in self.__dict__.items() if "source_" in field and val][0]
                setattr(target, "notizen_sonstiger_manifestverlust", ", ".join([s for s in getattr(target, "notizen_sonstiger_manifestverlust", "").split(", ") if s and s != source]))
                target.save(update_fields=[field, "notizen_sonstiger_manifestverlust"])
            else:
                target.save(update_fields=[field])

        # additional 'logging' for money transaction
        if self.target_fieldname == "cards.Card.money":
            Transaction.objects.create(
                sender=target if self.wertaenderung > 0 else None,
                receiver=target if self.wertaenderung <= 0 else None,
                amount=math.fabs(self.wertaenderung),
                reason=f"Deaktivieren des Effekts von {', '.join([getattr(self, field.replace('_id', '')).__str__() for field, val in self.__dict__.items() if 'source_' in field and val])}",
            )

        # set is_active (& save)
        self.is_active = False
        if save:
            self.save(update_fields=["is_active"])
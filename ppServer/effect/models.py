from django.db import models
from django.forms import ValidationError


class AbstractEffect(models.Model):
    class Meta:
        ordering = ['target_fieldname']
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

        ("character.Charakter.geld", "Charakter: Geld"),
        ("character.Charakter.prestige", "Charakter: Prestige"),
        ("character.Charakter.verzehr", "Charakter: Verzehr"),
        ("character.Charakter.sanität", "Charakter: Sanität"),
        ("character.Charakter.glück", "Charakter: Glück"),
        ("character.Charakter.sonstiger_manifestverlust", "Charakter: Manifest"),

        ("character.Charakter.HPplus", "Charakter: kHP plus"),
        ("character.Charakter.HPplus_fix", "Charakter: kHP plus fix"),
        ("character.Charakter.HPplus_geistig", "Charakter: gHP plus"),
        ("character.Charakter.rang", "Charakter: Rang"),

        ("character.Charakter.crit_attack", "Charakter: Crit-Angriff"),
        ("character.Charakter.crit_defense", "Charakter: Crit-Verteidigung"),

        ("character.Charakter.initiative_bonus", "Charakter: Initiative-Bonus"),
        ("character.Charakter.reaktion_bonus", "Charakter: Reaktinsbonus"),
        ("character.Charakter.natürlicher_schadenswiderstand_bonus", "Charakter: nat. SchaWi-Bonus"),
        ("character.Charakter.astralwiderstand_bonus", "Charakter: AsWi-Bonus"),
        ("character.Charakter.manaoverflow_bonus", "Charakter: Manaoverflow-Bonus"),
    ]

    wertaenderung = models.IntegerField(null=False, blank=False)
    target_fieldname = models.CharField(choices=target_fieldname_enum)


    def __str__(self):
        
        addition = ""
        if "character.RelAttribut" in self.target_fieldname and getattr(self, "target_attribut", None):
            addition = self.target_attribut.__str__()
        elif "character.RelFertigkeit" in self.target_fieldname and getattr(self, "target_fertigkeit", None):
            addition = self.target_fertigkeit.__str__()

        return f"{self.wertaenderung} {self.get_target_fieldname_display()}{' (' + addition + ')' if addition else ''}"


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

        elif "character.Charakter" in self.target_fieldname and (getattr(self, "target_attribut", None) or getattr(self, "target_fertigkeit", None)):
            raise ValidationError("Attribut oder Fertigkeit unnötigerweise ausgewählt")



class Effect(AbstractEffect):
    class Meta:
        verbose_name = "Effekt"
        verbose_name_plural = "Effekte"

    target_attribut = models.ForeignKey("character.Attribut", on_delete=models.SET_DEFAULT, default=None, null=True, blank=True)
    target_fertigkeit = models.ForeignKey("character.Fertigkeit", on_delete=models.SET_DEFAULT, default=None, null=True, blank=True)

    source_vorteil = models.ForeignKey("character.Vorteil", on_delete=models.CASCADE, null=True, blank=True)
    source_nachteil = models.ForeignKey("character.Nachteil", on_delete=models.CASCADE, null=True, blank=True)



class RelEffect(AbstractEffect):
    class Meta:
        verbose_name = "Charakter-Effekt"
        verbose_name_plural = "Charakter-Effekte"

    target_char = models.ForeignKey("character.Charakter", on_delete=models.CASCADE, null=False, blank=False)
    target_attribut = models.ForeignKey("character.RelAttribut", on_delete=models.SET_DEFAULT, default=None, null=True, blank=True)
    target_fertigkeit = models.ForeignKey("character.RelFertigkeit", on_delete=models.SET_DEFAULT, default=None, null=True, blank=True)

    source_vorteil = models.ForeignKey("character.RelVorteil", on_delete=models.CASCADE, null=True, blank=True)
    source_nachteil = models.ForeignKey("character.RelNachteil", on_delete=models.CASCADE, null=True, blank=True)

    is_active = models.BooleanField(default=True, null=False, blank=False)

    def clean(self) -> None:
        super().clean()

        # source RelModel has to have a relation to self.target_char

        fieldnames = [field.replace("_id", "") for field, val in self.__dict__.items() if "source_" in field and val]
        wrong_relations = [fieldname for fieldname in fieldnames if getattr(self, fieldname).char != self.target_char]
        if len(wrong_relations):
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
        else:
            target = getattr(self, "target_char")

        # set change
        if self.target_fieldname.rsplit("_", 1)[-1] == "fix":
            setattr(target, field, self.wertaenderung)
            target.save(update_fields=[field])
        else:
            setattr(target, field, getattr(target, field, 0) + self.wertaenderung)
            target.save(update_fields=[field])

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
        else:
            target = getattr(self, "target_char")

        # set change
        if self.target_fieldname.rsplit("_", 1)[-1] == "fix":
            setattr(target, field, None)
            target.save(update_fields=[field])
        else:
            setattr(target, field, getattr(target, field, 0) - self.wertaenderung)
            target.save(update_fields=[field])

        # set is_active (& save)
        self.is_active = False
        if save:
            self.save(update_fields=["is_active"])
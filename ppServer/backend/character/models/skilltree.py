from django.core.validators import MaxValueValidator
from django.db import models

from shop.models import Magische_Ausrüstung

from .. import enums
from .gfs import Gfs
from .rel import *
from .relshop import RelMagische_Ausrüstung


class SkilltreeBase(models.Model):
    class Meta:
        verbose_name = "Base Skilltree"
        verbose_name_plural = "Base Skilltrees"

        ordering = ["stufe"]

    # stufe == 0: Bonus
    stufe = models.PositiveIntegerField(validators=[MaxValueValidator(10)], default=1, unique=True)
    sp = models.PositiveIntegerField(default=1)

    def __str__(self):
        return "Skilltree-Base Stufe {} ({} SP)".format(self.stufe, self.sp)


class GfsSkilltreeEntry(models.Model):
    class Meta:
        verbose_name = "Gfs Skilltree"
        verbose_name_plural = "Gfs Skilltrees"

        ordering = ["gfs", "base", "operation"]

    base = models.ForeignKey(SkilltreeBase, on_delete=models.CASCADE)
    gfs = models.ForeignKey(Gfs, on_delete=models.CASCADE)

    operation = models.CharField(max_length=1, choices=enums.skilltreeentry_enum, default="R", null=False, blank=False, help_text="wichtigstes Feld, bestimmt die Art des Eintrags und welche anderen Felder benötigt werden.")

    amount = models.SmallIntegerField(null=True, blank=True, help_text="für AP, FP, FG, SP, IP, TP und Anz. Zauber-slots, WP in Speizis/Wissis, Fertigkeitsboni, Crit und HP")
    stufe = models.SmallIntegerField(null=True, blank=True, help_text="für Zauber-slots und Stufen von Items")
    text = models.TextField(null=True, blank=True, help_text="für Vor-/Nachteilnotizen und alles nicht-implementierbare, z. B. Bonuseffekte bei Angriffen")

    fertigkeit = models.ForeignKey(Fertigkeit, on_delete=models.SET_NULL, null=True, blank=True, help_text="für Bonus in Fertigkeit und  ggf. Vor-/Nachteile wie Spezialisiert, die eine Fertigkeit brauchen.")
    vorteil = models.ForeignKey(Vorteil, on_delete=models.SET_NULL, null=True, blank=True, help_text="für neuen Vorteil")
    nachteil = models.ForeignKey(Nachteil, on_delete=models.SET_NULL, null=True, blank=True, help_text="für neuen Nachteil")
    
    wesenkraft = models.ForeignKey(Wesenkraft, on_delete=models.SET_NULL, null=True, blank=True, help_text="Für neue Wesenkraft")
    spezialfertigkeit = models.ForeignKey(Spezialfertigkeit, on_delete=models.SET_NULL, null=True, blank=True, help_text="Für neue Spezi oder WP in einer Spezi")
    wissensfertigkeit = models.ForeignKey(Wissensfertigkeit, on_delete=models.SET_NULL, null=True, blank=True, help_text="Für neue Wissi oder WP in einer Wissi")

    # shop
    magische_ausrüstung = models.ForeignKey(Magische_Ausrüstung, on_delete=models.SET_NULL, null=True, blank=True, help_text="Für ein magisches Item")

    def __str__(self):
        return f"{self.gfs} Stufe {self.base.stufe}: {self.get_operation_display()}"
    
    def __repr__(self) -> str:
        try:

            # AP, FP, FG, SP, IP, TP, Crit-Angriff, Crit-Verteidigung, körperliche HP, geistige HP, HP Schaden waff. Kampf,
            # Initiative fix, physische & astrale Reaktion, physischer Widerstand
            if self.operation in ["a", "f", "F", "p", "i", "t", "A", "V", "K", "G", "k", "I", "r", "N", "T"]:
                return f"+{self.amount} {self.get_operation_display()}"

            # Roleplay-Text
            if self.operation == "R": return f"{self.text} (Achtung, keine automatische Verechnung!)"
            
            # optional Stufe: Zauberslots, magisches Item
            if self.operation == "z": return f"{self.amount} Zauberslots" + (f" Stufe {self.stufe}" if self.stufe else "")
            if self.operation == "h": return f"{self.amount} {self.magische_ausrüstung.name}" + (f" Stufe {self.stufe}" if self.stufe else "")

            # Bonus in Fertigkeit
            if self.operation == "B": return f"+{self.amount} Bonus in {self.fertigkeit.titel}"

            # neu! (Wesenkraft, Spezi, Wissi)
            if self.operation == "e": return self.wesenkraft.titel
            if self.operation == "s": return self.spezialfertigkeit.titel
            if self.operation == "w": return self.wissensfertigkeit.titel

            # WP in Spezialfertigkeit & Wissensfertigkeit
            if self.operation == "S": return f"+{self.amount} WP in {self.spezialfertigkeit.titel}"
            if self.operation == "W": return f"+{self.amount} WP in {self.wissensfertigkeit.titel}"

            # new Teil
            if self.operation == "v": return f"{self.vorteil.titel}" + (f" {self.text}" if self.text else "") + (f" ({self.fertigkeit.titel})" if self.fertigkeit else "")
            if self.operation == "n": return f"{self.nachteil.titel}" + (f" {self.text}" if self.text else "") + (f" ({self.fertigkeit.titel})" if self.fertigkeit else "")
    
        except:
            return f"FORMAT ERROR bei {self.get_operation_display()}"

    def apply_to(self, char: "Charakter") -> None:

        # AP
        if self.operation == "a":
            char.ap += self.amount
            char.save(update_fields=["ap"])
            return
        # FP
        if self.operation == "f":
            char.fp += self.amount
            char.save(update_fields=["fp"])
            return
        # FG
        if self.operation == "F":
            char.fg += self.amount
            char.save(update_fields=["fg"])
            return
        # SP
        if self.operation == "p":
            char.sp += self.amount
            char.save(update_fields=["sp"])
            return
        # IP
        if self.operation == "i":
            char.ip += self.amount
            char.save(update_fields=["ip"])
            return
        # TP
        if self.operation == "t":
            char.tp += self.amount
            char.save(update_fields=["tp"])
            return
        # Crit-Angriff
        if self.operation == "A":
            char.crit_attack += self.amount
            char.save(update_fields=["crit_attack"])
            return
        # Crit-Verteidigung
        if self.operation == "V":
            char.crit_defense += self.amount
            char.save(update_fields=["crit_defense"])
            return
        # körperliche HP
        if self.operation == "K":
            char.HPplus += self.amount
            char.save(update_fields=["HPplus"])
            return
        # geistige HP
        if self.operation == "G":
            char.HPplus_geistig += self.amount
            char.save(update_fields=["HPplus_geistig"])
            return
        # HP Schaden waff. Kampf
        if self.operation == "k":
            if not char.wesenschaden_waff_kampf: char.wesenschaden_waff_kampf = 0
            if not char.wesenschaden_andere_gestalt: char.wesenschaden_andere_gestalt = 0
            char.wesenschaden_waff_kampf += self.amount
            char.wesenschaden_andere_gestalt += self.amount
            char.save(update_fields=["wesenschaden_waff_kampf", "wesenschaden_andere_gestalt"])
            return
        # Initiative fix
        if self.operation == "I":
            char.initiative_bonus += self.amount
            char.save(update_fields=["initiative_bonus"])
            return
        # physische Reaktion
        if self.operation == "r":
            char.physische_reaktion_bonus += self.amount
            char.save(update_fields=["physische_reaktion_bonus"])
            return
        # physischer Widerstand
        if self.operation == "N":
            char.physischer_widerstand_bonus += self.amount
            char.save(update_fields=["physischer_widerstand_bonus"])
            return
        # astrale Reaktion
        if self.operation == "T":
            char.astrale_reaktion_bonus += self.amount
            char.save(update_fields=["astrale_reaktion_bonus"])
            return

        # Roleplay-Text
        if self.operation == "R":
            if not char.processing_notes: char.processing_notes = {}
            if "skilltree" not in char.processing_notes: char.processing_notes["skilltree"] = []
            char.processing_notes["skilltree"].append(f"{self.__repr__()} (Skilltree St. {self.base.stufe})")
            char.save(update_fields=["processing_notes"])
            return
        
        # Zauberslots
        if self.operation == "z":
            stufe = self.stufe if self.stufe is not None else 30
            prev_amount = char.zauberplätze[str(stufe)] if stufe in char.zauberplätze else 0
            char.zauberplätze[str(stufe)] = prev_amount + self.amount
            char.save(update_fields=["zauberplätze"])
            return

        # magisches Item
        if self.operation == "h":
            rel, created = RelMagische_Ausrüstung.objects.get_or_create(item=self.magische_ausrüstung, char=char, stufe=self.stufe)
            rel.amount += self.amount
            rel.save(update_fields=["amount"])
            return

        # Bonus in Fertigkeit
        if self.operation == "B":
            relfert = RelFertigkeit.objects.get(char=char, fertigkeit=self.fertigkeit)
            relfert.fp_bonus += self.amount
            relfert.save(update_fields=["fp_bonus"])
            return

        # neu! Wesenkraft
        if self.operation == "e":
            RelWesenkraft.objects.get_or_create(char=char, wesenkraft=self.wesenkraft)
            return
        # neu! Spezi
        if self.operation == "s":
            RelSpezialfertigkeit.objects.get_or_create(char=char, spezialfertigkeit=self.spezialfertigkeit)
            return
        # neu! Wissi
        if self.operation == "w":
            RelWissensfertigkeit.objects.get_or_create(char=char, wissensfertigkeit=self.wissensfertigkeit)
            return

        # new Vorteil
        if self.operation == "v":
            RelVorteil.objects.create(char=char, teil=self.vorteil, fertigkeit=self.fertigkeit, notizen=self.text if self.text else None, is_sellable=self.vorteil.is_sellable)
            return
        # new Nachteil
        if self.operation == "n":
            RelVorteil.objects.create(char=char, teil=self.nachteil, fertigkeit=self.fertigkeit, notizen=self.text if self.text else None, is_sellable=self.nachteil.is_sellable)
            return
        
        # WP in Spezialfertigkeit
        created = False
        if self.operation == "S":
            rel, created = RelSpezialfertigkeit.objects.get_or_create(char=char, spezialfertigkeit=self.spezialfertigkeit)
            rel.stufe += self.amount
            rel.save(update_fields=["stufe"])
        # WP in Wissensfertigkeit
        if self.operation == "W":
            rel, created = RelWissensfertigkeit.objects.get_or_create(char=char, wissensfertigkeit=self.wissensfertigkeit)
            rel.stufe += self.amount
            rel.save(update_fields=["stufe"])

        # pay for new spezi/wissi where possible
        if created and char.sp > 0:
            char.sp -= 1
            char.save(update_fields=["sp"])

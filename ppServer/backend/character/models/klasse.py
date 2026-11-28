import math

from django.apps import apps
from django.db import models
from django.db.models import Subquery, OuterRef, F, Q, Exists, Value
from django.db.models.functions import Coalesce
from django.db.models.query import QuerySet


class Klasse(models.Model):
    class Meta:
        ordering = ['titel']
        verbose_name = "Klasse"
        verbose_name_plural = "Klassen"

    requirement = models.CharField(max_length=128, null=True, blank=True, help_text="Wird auch halbwegs zur Berechnung benutzt, also bitte nicht selbstständig ändern!")
    titel = models.CharField(max_length=30, null=False, default="")
    base_abilities = models.ManyToManyField("KlasseAbility")

    def __str__(self):
        return self.titel


class KlasseStufenplan(models.Model):
    class Meta:
        ordering = ['klasse', "stufe"]
        verbose_name = "Klasse-Stufenplan"
        verbose_name_plural = "Klasse-Stufenpläne"
        unique_together = ["klasse", "stufe"]

    klasse = models.ForeignKey(Klasse, on_delete=models.CASCADE)
    stufe = models.PositiveSmallIntegerField(null=False, blank=False)

    ap = models.PositiveSmallIntegerField(default=0)
    fp = models.PositiveSmallIntegerField(default=0)
    fg = models.PositiveSmallIntegerField(default=0)
    tp = models.PositiveSmallIntegerField(default=0)
    ip = models.PositiveSmallIntegerField(default=0)
    zauber = models.PositiveSmallIntegerField(default=0)
    ability = models.ForeignKey("KlasseAbility", on_delete=models.SET_NULL, null=True, blank=True)

    @staticmethod
    def get_own_KlasseStufenplan(char: "Charakter") -> QuerySet["KlasseStufenplan"]:
        RelKlasse = apps.get_model("character", "RelKlasse")
        return KlasseStufenplan.objects\
            .annotate(owned = Exists(RelKlasse.objects.filter(char=char, klasse=OuterRef("klasse"), stufe__gte=OuterRef("stufe"))))\
            .filter(owned=True)

    @staticmethod
    def get_choosable_KlasseStufenplan(char: "Charakter") -> list["KlasseStufenplan"]:
        # qs with all immediately-choosable-by-stufe-stufenpläne of all Klassen
        RelKlasse = apps.get_model("character", "relklasse")

        qs = KlasseStufenplan.objects\
            .prefetch_related("klasse__base_abilities")\
            .annotate(
                current_stufe = Coalesce(Subquery(RelKlasse.objects.filter(char=char, klasse=OuterRef("klasse")).values("stufe")), 0),
                min_stufe = Subquery(KlasseStufenplan.objects.filter(klasse=OuterRef("klasse")).values("stufe").order_by("stufe")[:1]),
                requirements_met = Value(True),
            )\
            .filter(
                # in new Klasse: 1st stufe
                (Q(current_stufe=0) & Q(stufe=F("min_stufe"))) |
                # in chosen Klasse: next stufe
                (~Q(current_stufe=0) & Q(stufe=F("current_stufe")+1))
            )
        
        
        # evaluate requirements

        # prepare fields to check
        attrs = {rel.attribut.titel: rel.aktuell() for rel in char.relattribut_set.prefetch_related("attribut").all()}
        fg = { rel.gruppe: rel.fg for rel in char.relgruppe_set.all() }
        fert = {rel.fertigkeit.titel: attrs[rel.fertigkeit.attribut.titel] + fg[rel.fertigkeit.gruppe] + rel.fp + rel.fp_bonus for rel in char.relfertigkeit_set.prefetch_related("fertigkeit__attribut").all()}

        calc_vals = {
            "Initiative": char.initiative,
            "astrale Reaktion": char.astrale_reaktion[0], # ignored string/dice component
            "physische Reaktion": char.physische_reaktion,
            "physischer Widerstand": char.physischer_widerstand[0], # ignored string/dice component
            "körperliche HP": char.kHP["total"],
            "geistige HP": char.gHP["total"],
        }
        fields = { **attrs, **fert, **calc_vals }

        # decide if requirements are met
        result_list: list["KlasseStufenplan"] = []
        for stufenplan in qs:
            field, _, value = stufenplan.klasse.requirement.rpartition(" ")
            stufenplan.requirements_met = fields[field] >= int(value) or stufenplan.stufe > stufenplan.min_stufe
            result_list.append(stufenplan)

        return result_list


class KlasseAbility(models.Model):
    class Meta:
        ordering = ["name"]
        verbose_name = "Klassen-Fähigkeit"
        verbose_name_plural = "Klassen-Fähigkeiten"

    name = models.CharField(max_length=100, null=False, unique=True, verbose_name="Fähigkeit")
    beschreibung = models.TextField(max_length=2000, null=False, verbose_name="Beschreibung")

    notizen = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.name

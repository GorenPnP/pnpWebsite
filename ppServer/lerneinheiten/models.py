from django.db import models
from django.db.models import Max

from colorfield.fields import ColorField


inhalt_object_enum = [
    ("t", "Text"),
    ("i", "Bild"),
    ("v", "Video"),
    ("a", "Tabelle"),
]

class Fach(models.Model):

    class Meta:
        ordering = [ "name"]
        verbose_name = "Fach"
        verbose_name_plural = "Fächer"

    name = models.CharField(max_length=128, unique=True)

    def __str__(self):
        return self.name


def next_einheit_number():
    return Einheit.objects.aggregate(nr = Max("number", default=0))["nr"] + 1
class Einheit(models.Model):
    class Meta:
        ordering = ["number"]
        verbose_name = "Lerneinheit"
        verbose_name_plural = "Lerneinheiten"


    number = models.PositiveIntegerField(default=next_einheit_number)   # is basically unique, but not enforced on db-level due to sorting in editor
    titel = models.CharField(max_length=256, unique=True)

    fach = models.ForeignKey(Fach, on_delete=models.SET_NULL, null=True, blank=True)
    klasse = models.PositiveSmallIntegerField(default=4)

    def __str__(self):
        return f"#{self.number} {self.titel}"
    

class Page(models.Model):
    class Meta:
        ordering = ["einheit__number", "number"]
        verbose_name = "Seite"
        verbose_name_plural = "Seiten"
        #unique_together = [("number", "einheit")]   # is basically unique, but not enforced on db-level due to sorting in editor

    type_enum = [
        ("i", "Lerninhalt"),

        ("lf", "Lückentext mit Freitext"),
        ("ls", "Lückentext mit Auswahl"),
        ("ld", "Lückentext mit Vorgabe"),

        ("do", "Sortieren"),
        ("dt", "Themen zuordnen"),
        ("dv", "Verbinden"),

        ("cs", "Single Choice"),
        ("cm", "Multiple Choice"),

        ("ft", "Freitext"),

        ("uc", "Zeichnen"),
    ]

    einheit = models.ForeignKey(Einheit, on_delete=models.CASCADE)
    number = models.PositiveSmallIntegerField(default=1)

    titel = models.CharField(max_length=256, unique=True)
    color = ColorField(default='#000000')

    type = models.CharField(max_length=2, choices=type_enum, null=False)
    content = models.JSONField(default=dict, blank=True)
    solution = models.JSONField(default=dict, blank=True)

    def __str__(self):
        return f"#{self.einheit.number}.{self.number} {self.titel}"

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


class Einheit(models.Model):
    class Meta:
        ordering = ["number"]
        verbose_name = "Lerneinheit"
        verbose_name_plural = "Lerneinheiten"

    next_number = lambda: Einheit.objects.aggregate(Max("nr", default=1))["max_nr"] + 1


    number = models.PositiveIntegerField(default=next_number, unique=True)
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
        unique_together = [("number", "einheit")]

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

    type = models.CharField(max_length=2, choices=type_enum)
    content = models.JSONField(default=dict)
    solution = models.JSONField(default=dict)

    def __str__(self):
        return f"#{self.einheit.number}.{self.number} {self.titel}"

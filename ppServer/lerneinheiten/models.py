from django.db import models
from django.db.models import Max

from colorfield.fields import ColorField

from character.models import Spieler

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
    


def pageimage_path(instance, filename): 
    # file will be uploaded to path: 
    return f'lerneinheiten/page_image/{instance.page.id}/{filename}' 

class PageImage(models.Model):
    class Meta:
        ordering = ["page"]

    image = models.ImageField(upload_to=pageimage_path)
    page = models.ForeignKey("Page", on_delete=models.CASCADE)

    # will be set for a spieler-saved image, None for editor-images
    spielerPage = models.ForeignKey("SpielerPage", on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.image.url

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
    color = ColorField(default='#000000', verbose_name="Farbe")

    type = models.CharField(max_length=2, choices=type_enum, null=False)
    content = models.JSONField(default=dict, blank=True, verbose_name="Inhalt")
    solution = models.JSONField(default=dict, blank=True, verbose_name="Musterlösung")

    def __str__(self):
        return f"#{self.einheit.number}.{self.number} {self.titel}"



class SpielerEinheit(models.Model):
    class Meta:
        unique_together = [("spieler", "einheit")]

    spieler = models.ForeignKey(Spieler, on_delete=models.CASCADE)
    einheit = models.ForeignKey(Einheit, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.einheit} - {self.spieler}"


class SpielerPage(models.Model):
    class Meta:
        ordering = ["spieler", "page"]
        verbose_name = "Antwort"
        verbose_name_plural = "Antworten"
        unique_together = [("spieler", "page")]

    page = models.ForeignKey(Page, on_delete=models.CASCADE)
    spieler = models.ForeignKey(Spieler, on_delete=models.CASCADE)

    answer = models.JSONField(default=dict, null=False, blank=False)

    def __str__(self):
        return f"Antwort von {self.spieler} zu {self.page}"


class Inquiry(models.Model):
    class Meta:
        ordering = ["spieler", "page"]
        verbose_name = "Nachfrage"
        verbose_name_plural = "Nachfragen"
        unique_together = [("spieler", "page")]

    page = models.ForeignKey(Page, on_delete=models.CASCADE)
    spieler = models.ForeignKey(Spieler, on_delete=models.CASCADE)

    question = models.TextField(null=False, blank=True, verbose_name="Feedback, Nachfrage oder allgemeine Verwirrtheit")
    response = models.TextField(null=True, blank=True, verbose_name="Spielleiter-Antwort")

    def __str__(self):
        return f"Nachfrage von {self.spieler} zu {self.question}"

from django.db import models

from character.models import Spieler


class File(models.Model):

    class Meta:
        verbose_name = 'File'
        verbose_name_plural = 'Files'
        ordering = ['file']

    def __str__(self):
        return self.file.name

    file = models.FileField(upload_to='files/')


class Topic(models.Model):

    class Meta:
        verbose_name = 'Thema'
        verbose_name_plural = 'Themen'
        ordering = ['titel']

    def __str__(self):
        return self.titel

    titel = models.CharField(max_length=200)
    files = models.ManyToManyField(File)

    sichtbarkeit_eingeschränkt = models.BooleanField(default=False)
    sichtbar_für = models.ManyToManyField(Spieler, blank=True)

    beschreibung = models.CharField(max_length=1000, blank=True)

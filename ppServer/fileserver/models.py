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
    show_in_admin = models.BooleanField(default=True)


class Story(models.Model):

    class Meta:
        verbose_name = 'Story'
        verbose_name_plural = 'Storys'
        ordering = ['titel']

    def __str__(self):
        return self.titel

    titel = models.CharField(max_length=200, unique=True)
    files = models.ManyToManyField(File)

    sichtbar_für = models.ManyToManyField(Spieler, blank=True)

    beschreibung = models.CharField(max_length=1000, blank=True)


class Map(models.Model):

    class Meta:
        verbose_name = 'Map'
        verbose_name_plural = 'Maps'
        ordering = ['titel']

    def __str__(self):
        return self.titel

    titel = models.CharField(max_length=200)
    files = models.ManyToManyField(File)

    sichtbar_für = models.ManyToManyField(Spieler, blank=True)

    beschreibung = models.CharField(max_length=1000, blank=True)

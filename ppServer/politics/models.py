from django.db import models

from colorfield.fields import ColorField
from django_resized import ResizedImageField

class Party(models.Model):
    class Meta:
        verbose_name = "Partei"
        verbose_name_plural = "Parteien"

        ordering = ["rightwing_tendency", "name"]

    rightwing_tendency = models.FloatField(default=0, unique=True)
    color = ColorField(default='#ffffff')

    name = models.TextField()
    abbreviation = models.CharField(max_length=10)
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.abbreviation or self.name
    
    def serialize(self):
        fields = [
            "color",
            "name",
            "abbreviation",
            "description",
            "rightwing_tendency",
        ]
        return {
            **{field: getattr(self, field) for field in fields},
            "politicians": [pol.serialize() for pol in self.politician_set.all()]
        }


class Politician(models.Model):
    class Meta:
        verbose_name = "Politiker*in"
        verbose_name_plural = "Politiker*innen"

        ordering = ['name', '-birthyear']

    portrait = ResizedImageField(size=[64, 64], null=True, blank=True)
    name = models.CharField(max_length=300, null=True, blank=True)

    is_party_lead = models.BooleanField(default=False)
    party = models.ForeignKey(Party, on_delete=models.CASCADE, null=True, blank=True)

    genere = models.CharField(max_length=64, null=True, blank=True)
    birthyear = models.BigIntegerField(null=True, blank=True)

    def __str__(self):
        return self.name or '-'
    
    def serialize(self):
        fields = [
            "name",
            "is_party_lead",
            "genere",
            "birthyear",
        ]
        return {
            "portrait": self.portrait.url if self.portrait else None,
            **{field: getattr(self, field) for field in fields},
        }
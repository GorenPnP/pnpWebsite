from django.db import models


class Level(models.Model):
    class Meta:
        ordering = ['name']
        verbose_name = "Level"
        verbose_name_plural = "Levels"

    name = models.CharField(max_length=200, null=False, blank=False, unique=True)
    width = models.PositiveSmallIntegerField(default=15, null=False, blank=False)
    height = models.PositiveSmallIntegerField(default=6, null=False, blank=False)

    tiles = models.JSONField(default=list)

    def __str__(self):
        return self.name
from django.db import models

from colorfield.fields import ColorField


class Category(models.Model):
    class Meta:
        ordering = ["name"]

    color = ColorField(default='#ffffff', verbose_name="Farbe")
    textColor = ColorField(default='#000000', verbose_name="Textfarbe")

    name = models.CharField(max_length=128, unique=True)


class TimeInterval(models.Model):
    class Meta:
        ordering = ["start", "end", "category"]
        constraints = [
            models.CheckConstraint(
                check=models.Q(start__lte=models.F("end")), name="ends_not_earlier_than_start"
            ),
        ]

    start = models.DateTimeField()
    end = models.DateTimeField()

    category = models.ForeignKey(Category, on_delete=models.CASCADE)

from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

class Publisher(models.Model):
    class Meta:
        verbose_name = "Herausgeber"
        verbose_name_plural = "Herausgeber"

        ordering = ["name"]

    name = models.TextField()

    def __str__(self):
        return self.name


class Category(models.Model):
    class Meta:
        verbose_name = "Kategorie"
        verbose_name_plural = "Kategorien"

        ordering = ["name"]

    name = models.TextField()
    beschreibung = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.name


class News(models.Model):
    class Meta:
        verbose_name = "News"
        verbose_name_plural = "News"

        ordering = ['-creation', '-importance']

    titel = models.CharField(max_length=300)
    summary = models.CharField(max_length=300)
    text = models.TextField(null=True, blank=True)

    importance = models.PositiveSmallIntegerField(default=3, help_text="5 has highest importance, 1 lowest", validators=[MinValueValidator(1), MaxValueValidator(5)])
    publisher = models.ForeignKey(Publisher, on_delete=models.SET_NULL, null=True, blank=True)
    categories = models.ManyToManyField(Category)

    creation = models.DateField(auto_now_add=True)
    last_edit = models.DateField(auto_now=True)

    breaking_news = models.BooleanField(default=False)
    published = models.BooleanField(default=False)

    def __str__(self):
        return self.titel

from django.db import models

class Request(models.Model):
    class Meta:
        verbose_name = "Anfrage"
        verbose_name_plural = "Anfragen"

        ordering= ["-zeit"]

    zeit = models.DateTimeField(auto_now_add=True)
    pfad = models.CharField(max_length=500, default="/", null=False, blank=False)
    antwort = models.PositiveSmallIntegerField(default=200, null=False, blank=False)
    methode = models.CharField(max_length=8, default="GET", null=False, blank=False)
    user = models.CharField(default="", max_length=200, null=False, blank=False)
    user_agent = models.CharField(max_length=200)

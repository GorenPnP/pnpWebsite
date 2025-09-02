from django.db import models


kind_enum = [
    ("s", "Shop"),
    ("u", "Auswertung"),
    ("i", "Stufenaufstieg"),
    ("l", "Klasse verteilt"),

    ("o", "Sonderangebot"),
    ("a", "Attribute"),
    ("f", "Fertigkeiten"),
    ("h", "HPcp"),

    ("g", "mehr Geld"),
    ("c", "mehr CP"),
    ("b", "mehr EP"),
    ("p", "mehr SP"),
    ("r", "mehr Rang"),
    ("e", "weniger Geld"),
    ("k", "weniger SP"),

    ("n", "neuer Nachteil"),
    ("x", "Nachteil weg"),
    ("y", "neuer Vorteil"),
    ("z", "Vorteil weg"),

    ("t", "Skilltree"),
    ("m", "Manaverbrauch abgezogen"),
    ("v", "Magie verloren"),

    ("d", "Quiz-Punkte für SP"),
    ("j", "Inventar-Item verbraucht"),
    ("q", "Inventar-Item angelegt"),
    ("w", "Inventar-Item verkauft"),
]


class Log(models.Model):

    class Meta:
        verbose_name = "Log"
        verbose_name_plural = "Logs"
        ordering = ['-timestamp']

    spieler = models.ForeignKey("character.Spieler", on_delete=models.CASCADE)
    char = models.ForeignKey("character.Charakter", on_delete=models.CASCADE, verbose_name="Charakter")
    art = models.CharField(max_length=1, choices=kind_enum)
    kosten = models.TextField()
    notizen = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True, blank=True, null=True)

    def __str__(self):
        return "In Kategorie {} für {} von {} geändert".format(self.get_art_display(), self.char.name, self.spieler.name)

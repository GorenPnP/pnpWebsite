from django.db import models

from character.models import Spieler, Charakter

kind_enum = [("s", "Shop"),
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
             ]


class Log(models.Model):

    class Meta:
        ordering = ['-timestamp']

    spieler = models.ForeignKey(Spieler, on_delete=models.CASCADE)
    char = models.ForeignKey(Charakter, on_delete=models.CASCADE)
    art = models.CharField(max_length=1, choices=kind_enum)
    kosten = models.TextField()
    notizen = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True, blank=True)

    def __str__(self):
        return "In Kategorie {} für {} von {} geändert".format(self.get_art_display(), self.char.name, self.spieler.name)

from datetime import datetime

from django.contrib.auth import get_user_model
from django.db import models


class Tag(models.Model):

    class Meta:
        verbose_name = "Tag"
        verbose_name_plural = "Tags"
        ordering = ["name"]

    name = models.CharField(max_length=10, unique=True)

    def __str__(self):
        return self.name


class Day(models.Model):

    User = get_user_model()

    class Meta:
        verbose_name = "Terminabsprache"
        verbose_name_plural = "Terminabsprachen"
        ordering = ["date"]

    date = models.DateField(unique=True, default=datetime.today)
    proposals = models.ManyToManyField(User, through="Proposal")

    open_for_participation = models.BooleanField(default=True)

    max_players = models.PositiveSmallIntegerField(default=4, null=False, blank=False)
    max_waitinglist = models.PositiveSmallIntegerField(default=2, null=False, blank=False)

    def __str__(self):
        return "{} ({})".format(self.date, self.status())


    def status(self):

        if self.is_fully_blocked(): return "blocked"

        # by state and existing appointment
        try:
            if self.appointment: return "takes-place"
        except: pass
        if not self.open_for_participation: return "cancelled"

        # state is 'open for participation'. Differ by player count
        player_count = self.proposals.count()
        if player_count == 0: return "free"
        if player_count < self.max_players: return "open"
        if player_count < self.max_players + self.max_waitinglist: return "half"
        return "full"

    def to_dict(self):
        blockedTime = self.blockedTime()
        blocked = None
        if blockedTime:
            blocked = {
                "name": blockedTime.name,
                "start": blockedTime.start,
                "end": blockedTime.end,
            }

        appointment = None
        if self.status() == "takes-place":
            appointment = {
                "title": self.appointment.title,
                "tags": ", ".join([t.name for t in self.appointment.tags.all()]),
                "start": self.appointment.start
            }

        def format_spieler(user: User):
            name = user.first_name
            if user.last_name:
                name += " " + user.last_name
            return name if name else user.username

        return {
            "date": self.date,
            "open_for_participation": self.open_for_participation,
            "proposals": [format_spieler(p.player) for p in Proposal.objects.filter(day=self).order_by("order")],
            "appointment": appointment,
            "blocked_time":  blocked,
            "status": self.status()
        }
    
    def blockedTime(self):
        try:
            return self.blockedtime
        except: return None

    def is_fully_blocked(self):
        blockedTime = self.blockedTime()
        return blockedTime and blockedTime.start <= min_time() and blockedTime.end >= max_time()


def default_time():
    return datetime(2000, 1, 1, 14, 0).time()

def min_time():
    return datetime(2000, 1, 1, 0, 0).time()

def max_time():
    return datetime(2000, 1, 1, 23, 59, 59).time()



class Appointment(models.Model):
    class Meta:
        verbose_name = "Termin"
        verbose_name_plural = "Termine"
        ordering = ["day"]

    day = models.OneToOneField(Day, on_delete=models.CASCADE)

    title = models.CharField(max_length=200)
    tags = models.ManyToManyField(Tag)
    start = models.TimeField(unique=True, default=default_time)



class Proposal(models.Model):

    class Meta:
        verbose_name = "Terminvorschlag"
        verbose_name_plural = "Terminvorschläge"
        ordering = ["day"]

    day = models.ForeignKey(Day, on_delete=models.CASCADE)

    player = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    order = models.PositiveSmallIntegerField()

    start = models.TimeField(default=default_time)
    note = models.TextField(blank=True, null=True)

    def __str__(self):
        return "#{}: {}".format(self.order, self.player)
        

class BlockedTime(models.Model):

    class Meta:
        verbose_name = "Blockierter Zeitraum"
        verbose_name_plural = "Blockierte Zeiträume"
        ordering = ["day"]

    day = models.OneToOneField(Day, on_delete=models.CASCADE)

    name = models.CharField(max_length=200, default="")
    start = models.TimeField(default=min_time)
    end = models.TimeField(default=max_time)

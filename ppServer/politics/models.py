from django.db import models

from colorfield.fields import ColorField
from django_resized import ResizedImageField
from markdownfield.models import MarkdownField, RenderedMarkdownField
from markdownfield.validators import VALIDATOR_STANDARD

class Party(models.Model):
    class Meta:
        verbose_name = "Partei"
        verbose_name_plural = "Parteien"

        ordering = ["leftwing_tendency", "name"]

    leftwing_tendency = models.FloatField(default=0, unique=True)
    color = ColorField(default='#ffffff')
    textColor = ColorField(default='#000000')

    name = models.TextField()
    abbreviation = models.CharField(max_length=10)
    program = MarkdownField(rendered_field='program_rendered', validator=VALIDATOR_STANDARD, null=True, blank=True)
    program_rendered = RenderedMarkdownField(null=True)

    def __str__(self):
        return self.abbreviation or self.name
    
    def serialize(self, populate_politician=False):
        fields = [
            "id",
            "color",
            "textColor",
            "name",
            "abbreviation",
            "program_rendered",
            "leftwing_tendency",
        ]
        return {
            **{field: getattr(self, field) for field in fields},
            "politicians": [pol.serialize() for pol in self.politician_set.all()] if populate_politician else list(self.politician_set.values_list("id", flat=True))
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
    member_of_parliament = models.BooleanField(default=True)

    genere = models.CharField(max_length=64, null=True, blank=True)
    birthyear = models.BigIntegerField(null=True, blank=True)

    def __str__(self):
        return self.name or '-'
    
    def serialize(self, populate_party=False):
        fields = [
            "id",
            "name",
            "is_party_lead",
            "member_of_parliament",
            "genere",
            "birthyear",
        ]
        return {
            "portrait": self.portrait.url if self.portrait else None,
            **{field: getattr(self, field) for field in fields},
            "party": self.party.serialize() if populate_party else self.party.id
        }


class LegalAct(models.Model):
    class Meta:
        verbose_name = "Gesetz"
        verbose_name_plural = "Gesetze"

        ordering = ['code', 'paragraph']

    code = models.CharField(max_length=128, help_text="Gesetzbuch")
    paragraph = models.CharField(max_length=16)

    text = MarkdownField(rendered_field='text_rendered', validator=VALIDATOR_STANDARD)
    text_rendered = RenderedMarkdownField(null=False)

    votes = models.ManyToManyField(Politician, through="PoliticianVote")
    voting_done = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.code} §{self.paragraph}"
    
    def serialize(self, populate_votes=False):
        fields = [
            "id",
            "code",
            "paragraph",
            "text",
            "text_rendered",
            "voting_done",
        ]
        return {
            **{field: getattr(self, field) for field in fields},
            "votes": [v.serialize(populate_politician=True) for v in self.politicianvote_set.all()] if populate_votes else list(self.politicianvote_set.values_list("id", flat=True)),
        }
    

class PoliticianVote(models.Model):
    class Meta:
        verbose_name = "Abstimmung"
        verbose_name_plural = "Abstimmungen"

        ordering = ['legal_act', 'politician']
        unique_together = ("legal_act", "politician")

    VOTE_ENUM = [
        ("y", "Ja"),
        ("n", "Nein"),
        ("e", "Enthaltung"),
        ("a", "nicht anwesend"),
    ]

    legal_act = models.ForeignKey(LegalAct, on_delete=models.CASCADE)
    politician = models.ForeignKey(Politician, on_delete=models.CASCADE)

    vote = models.CharField(max_length=1, choices=VOTE_ENUM, default="a")

    def serialize(self, populate_politician=False, populate_legal_act=False):
        return {
            "vote": self.vote,
            "legal_act": self.legal_act.serialize() if populate_legal_act else self.legal_act.id,
            "politician": self.politician.serialize() if populate_politician else self.politician.id,
        }
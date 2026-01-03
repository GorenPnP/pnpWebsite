from datetime import datetime, timezone

from django.db import models
from django.db.models import F, Subquery, OuterRef, Q, Count, Value
from django.db.models.functions import Coalesce
from django.utils.text import slugify

from django_resized import ResizedImageField

from character.models import Spieler
from ppServer.utils import ConcatSubquery


class SumSubquery(Subquery):
    template = '(SELECT SUM("%(sum_field)s") FROM (%(subquery)s) subquery)'

    def __init__(self, sum_field, queryset, output_field, **extra):
        super().__init__(queryset, output_field, sum_field=sum_field, **extra)


class Account(models.Model):
    class Meta:
        ordering = ["spieler", "name"]
        verbose_name = "Person"
        verbose_name_plural = "Personen"
        
    avatar = ResizedImageField(size=[300, 300], upload_to='httpChat/avatar/', crop=['middle', 'center'], null=True, blank=True)

    spieler = models.ForeignKey(Spieler, on_delete=models.SET_NULL, blank=False, null=True)
    name = models.CharField(max_length=200, null=False, blank=False, unique=True)
    slug = models.SlugField(unique=True)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name
    
    def get_avatar_url(self):
        return self.avatar.url if self.avatar else "/static/res/img/goren_logo.png"
    
    class UnreadMessagesManager(models.Manager):
        def load_unread_messages(self):
            """ preloads number of unread messages """

            unread_message_qs = ChatroomAccount.objects.load_unread_messages().prefetch_related("account").filter(account__id=OuterRef("id"))
            return self\
                .annotate(
                    unread_messages = Coalesce(SumSubquery("unread_messages", queryset=unread_message_qs, output_field=models.IntegerField()), Value(0))
                )
    objects = UnreadMessagesManager()



def ancient_datetime():
    return datetime(1990, 6, 1, 0, 0, 0, 0, tzinfo=timezone.utc)

class ChatroomAccount(models.Model):
    class Meta:
        verbose_name = "Account"
        verbose_name_plural = "Accounts"

        ordering = ["account", "chatroom"]
        unique_together = ("account", "chatroom")

    chatroom = models.ForeignKey("Chatroom", on_delete=models.CASCADE)
    account = models.ForeignKey(Account, on_delete=models.CASCADE)

    latest_access = models.DateTimeField(default=ancient_datetime)

    def __str__(self):
        return self.account.name
    
    class UnreadMessagesManager(models.Manager):
        def load_unread_messages(self):
            """ preloads number of unread messages """
            return self\
                .prefetch_related("chatroom_set__message_set__author")\
                .annotate(
                    unread_messages = Coalesce(
                        Count("chatroom__message", distinct=True, filter=
                            ~Q(chatroom__message__author__id=F("account__id")) &        # .exclude(author=account)
                            Q(chatroom__message__type="m") &                            # type is a written message, no info or sth.
                            Q(chatroom__message__created_at__gte=F("latest_access"))    # message that is younger than the last time the account opened the chatroom
                        ),
                        Value(0)
                    )
                )
    objects = UnreadMessagesManager()


class Chatroom(models.Model):
    class Meta:
        ordering = ["titel"]
        verbose_name = "Chatroom"
        verbose_name_plural = "Chatrooms"

    titel = models.CharField(max_length=200, null=True, blank=True)

    accounts = models.ManyToManyField(Account, through=ChatroomAccount)

    def __str__(self):
        if self.titel: return self.titel

        return ", ".join([a.name for a in self.accounts.all().order_by("name")])

    def get_avatar_urls(self, excluding_account: Account=None):
        qs = self.accounts.all()
        
        if excluding_account:
            qs = qs.exclude(id=excluding_account.id)
        return [a.get_avatar_url() for a in qs]
    

    class TitleManager(models.Manager):
        def load_title(self, account: Account):
            """ preloads a computed chatroom-title (field 'titel', fallback is all account names, except for the param 'account') """
            return self\
                .annotate(
                    final_title = Coalesce(
                        "titel",
                        ConcatSubquery(
                            Account.objects
                                .filter(chatroom__id=OuterRef("id"))
                                .exclude(id=account.id)
                                .values("name")
                                .order_by("name"),
                            separator=", ")
                    )
                )
    objects = TitleManager()
    

class Message(models.Model):

    class Meta:
        verbose_name = "Nachricht"
        verbose_name_plural = "Nachrichten"

        ordering = ["chatroom", "created_at"]

    choices = [('m', "Message"), ("i", "Info")]

    type = models.CharField(choices=choices, default="m", max_length=1)
    text = models.CharField(max_length=2000)
    author = models.ForeignKey(Account, on_delete=models.SET_NULL, null=True, related_name="author")

    chatroom = models.ForeignKey(Chatroom, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "{} (von {})".format(self.text[:47] + (self.text[:47] and "..."), self.author)

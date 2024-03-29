from django import forms
from django.db.models import Count

from markdownfield.forms import MarkdownFormField
from markdownfield.widgets import MDEWidget

from .models import Account, Chatroom, Message

class MessageForm(forms.Form):
    # text = MarkdownFormField(widget=MDEWidget)
    text = forms.CharField(widget=MDEWidget)



class AccountForm(forms.ModelForm):
    class Meta:
        model = Account
        fields = ["avatar", "name"]


class M2MSelect(forms.SelectMultiple):
    allow_multiple_selected = False

class ChatroomForm(forms.ModelForm):


    class Meta:
        model = Chatroom
        fields = ["accounts"]
        widgets = {"accounts": M2MSelect()}
        labels = {
            "accounts": "Kontakt"
        }

    def __init__(self, exclude_account: Account=None, *args, **kwargs):
        super().__init__(*args, **kwargs)

        qs = Account.objects.all()
        if exclude_account:
            # exclude all accounts that share a 2-person private_chatroom with exclude_account. Including that account itself. 
            private_chatrooms = Chatroom.objects\
                .annotate(num=Count('accounts'))\
                .filter(accounts=exclude_account, num=2)

            qs = qs.exclude(chatroom__in=private_chatrooms)

        self.fields['accounts'].queryset = qs



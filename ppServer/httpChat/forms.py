from django import forms

from .models import Account, Chatroom

class AccountForm(forms.ModelForm):
    class Meta:
        model = Account
        fields = ["avatar", "name"]


class M2MSelect(forms.SelectMultiple):
    allow_multiple_selected = False

class ChatroomForm(forms.ModelForm):


    class Meta:
        model = Chatroom
        fields = ["titel", "accounts"]
        widgets = {"accounts": M2MSelect()}
        labels = {
            "accounts": "Kontakt"
        }

    def __init__(self, exclude_account: Account=None, *args, **kwargs):
        super().__init__(*args, **kwargs)

        qs = Account.objects.all()
        if exclude_account:
            # exclude all accounts that share a chatroom with  exclude_account. Including itself. 
            qs = qs.exclude(chatroom__accounts=exclude_account)

        self.fields['accounts'].queryset = qs



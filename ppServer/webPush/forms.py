from django import forms
from django.contrib.auth.models import User
from django.db.models import Exists, OuterRef

from push_notifications.models import WebPushDevice
from character.models import Spieler

from .models import *


class RegisterWebPushDeviceForm(forms.ModelForm):
    class Meta:
        model = WebPushDevice
        fields = ["registration_id", "p256dh", "auth", ] # "browser", "application_id", "name", "user", "active",


class PushSettingsForm(forms.ModelForm):
    class Meta:
        model = PushSettings
        fields = ["chat", "news", "polls", "quiz", "changelog", "politics"]


class SendMessageForm(forms.Form):

    title = forms.CharField(help_text="optionaler Titel der Nachricht", required=False)
    message = forms.CharField(widget=forms.widgets.Textarea, required=True)
    tag = forms.ChoiceField(required=False, choices=tuple((i.value, i.name) for i in PushTag), help_text="Der Browser ersetzt die letzte Nachricht mit dem Tag durch diese, anstatt beide Nachrichten gleichzeitig anzuzeigen")

    recipients = forms.ModelMultipleChoiceField(
        queryset=User.objects.annotate(keep=Exists(WebPushDevice.objects.filter(user__pk=OuterRef("pk")))).filter(keep=True),
        widget=forms.widgets.CheckboxSelectMultiple,
        label="Nachricht senden an",
        required=True,
    )


class UserSettingsForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["username", "first_name", "last_name"]

class SpielerSettingsForm(forms.ModelForm):
    class Meta:
        model = Spieler
        fields = ["geburtstag", "language"]

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.fields["geburtstag"].help_text = "Datumsformat ist tt.mm.jjjj"
            


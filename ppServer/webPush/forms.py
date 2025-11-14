from django import forms
from django.contrib.auth.models import User
from django.db.models import Exists, OuterRef

from crispy_forms.layout import Layout, Div, Field

from base.crispy_form_decorator import crispy
from character.models import Spieler
from push_notifications.models import WebPushDevice

from .models import *


class RegisterWebPushDeviceForm(forms.ModelForm):
    class Meta:
        model = WebPushDevice
        fields = ["registration_id", "p256dh", "auth", ] # "browser", "application_id", "name", "user", "active",


@crispy(form_tag=False)
class PushSettingsForm(forms.ModelForm):
    class Meta:
        model = PushSettings
        fields = ["chat", "news", "polls", "quiz", "changelog", "politics"]


@crispy(form_tag=False)
class SendMessageForm(forms.Form):

    title = forms.CharField(help_text="optionaler Titel der Nachricht", required=False, label="Titel")
    message = forms.CharField(widget=forms.widgets.Textarea, required=True, label="Nachricht")
    tag = forms.ChoiceField(required=False, choices=tuple((i.value, i.name) for i in PushTag), help_text="Der Browser ersetzt die letzte Nachricht mit dem Tag durch diese, anstatt beide Nachrichten gleichzeitig anzuzeigen")

    recipients = forms.ModelMultipleChoiceField(
        queryset=User.objects.annotate(keep=Exists(WebPushDevice.objects.filter(user__pk=OuterRef("pk")))).filter(keep=True),
        widget=forms.widgets.CheckboxSelectMultiple,
        label="Nachricht senden an",
        required=True,
    )

    def get_layout(self):
        return Layout(
            Div(
                Field('title', wrapper_class='col-12 col-sm-8'),
                Field('tag', wrapper_class='col-12 col-sm-4'),
            css_class='row'),
            "message", "recipients",
        )


@crispy(form_tag=False)
class UserSettingsForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["username", "first_name", "last_name"]
    
    def get_layout(self):
        return Layout(
            "username",
            Div(
                Field('first_name', wrapper_class='col-12 col-sm'),
                Field('last_name', wrapper_class='col-12 col-sm'),
            css_class='row')
        )


@crispy(form_tag=False)
class SpielerSettingsForm(forms.ModelForm):
    class Meta:
        model = Spieler
        fields = ["geburtstag", "language"]

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.fields["geburtstag"].help_text = "Datumsformat ist tt.mm.jjjj"


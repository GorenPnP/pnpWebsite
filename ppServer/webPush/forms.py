from django import forms

from push_notifications.models import WebPushDevice


class RegisterWebPushDeviceForm(forms.ModelForm):
    class Meta:
        model = WebPushDevice
        fields = ["registration_id", "p256dh", "auth", ] # "browser", "application_id", "name", "user", "active",
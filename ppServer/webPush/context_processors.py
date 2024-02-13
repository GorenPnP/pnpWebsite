from django.conf import settings # import the settings file
from django.urls import reverse

def push_settings(request):
    # return the value you want as a dictionary. you may add multiple values in there.
    return {
        'PUSH_NOTIFICATION_KEY': settings.PUSH_NOTIFICATION_KEY,
        'PUSH_SUBSCRIBE_USER_ENDPOINT': reverse("web_push:subscribe_user"),
    }
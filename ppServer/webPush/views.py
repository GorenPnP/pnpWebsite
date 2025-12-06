import json

from django.contrib import messages
from django.http.request import HttpRequest as HttpRequest
from django.http.response import HttpResponse as HttpResponse, JsonResponse
from django.shortcuts import redirect, render, get_object_or_404
from django.views.decorators.http import require_POST
from django.views.generic.base import TemplateView

from push_notifications.models import WebPushDevice

from ppServer.decorators import verified_account
from ppServer.mixins import SpielleitungOnlyMixin, VerifiedAccountMixin
from ppServer.settings import PUSH_NOTIFICATION_KEY

from .forms import *
from .models import *


class SettingView(VerifiedAccountMixin, TemplateView):
	template_name = "webPush/settings.html"
	object = None

	def get_object(self):
		self.object = self.object or get_object_or_404(PushSettings, user=self.request.user)
		return self.object

	def get(self, request):
		context = {
			"topic": "Einstellungen",
			"profile_forms": [UserSettingsForm(instance=self.request.user), SpielerSettingsForm(instance=self.request.spieler.instance)],
			"form": PushSettingsForm(instance=self.get_object()),
		}
		return render(request, self.template_name, context)
	
	def post(self, request):
		spieler_form = SpielerSettingsForm(request.POST, instance=request.spieler.instance)
		user_form = UserSettingsForm(request.POST, instance=request.user)

		spieler_form.full_clean()
		user_form.full_clean()
		if spieler_form.is_valid() and user_form.is_valid():
			user_form.save()
			spieler_form.save()
			messages.success(request, "Dein Profil wurde gespeichert")
			return redirect("web_push:settings")

		# on form error
		messages.error(request, "Fehler beim Speichern des Profils")
		context = {
			"topic": "Einstellungen",
			"profile_forms": [user_form, spieler_form],
			"form": PushSettingsForm(instance=self.get_object()),
		}
		return render(request, self.template_name, context)


class TestView(SpielleitungOnlyMixin, TemplateView):
	template_name = "webPush/testpage.html"

	def get(self, request: HttpRequest) -> HttpResponse:
		return render(request, self.template_name, {"app_server_key": PUSH_NOTIFICATION_KEY, "form": SendMessageForm()})

	def post(self, request):
		form = SendMessageForm(request.POST)
		form.full_clean()
		if not form.is_valid():
			# error
			messages.error(request, "neue Nachricht hatte ein seltsames Format oder war nicht vollständig")
			messages.error(request, f"{form.errors}")
		else:
			# success

			# send messages
			users = form.cleaned_data["recipients"]
			del form.cleaned_data["recipients"]
			results = PushSettings.send_message(users, **form.cleaned_data)

			# logging
			success = [r for r in results if "success" in r]
			error = [r for r in results if "failure" in r]

			print("Errors on send:", error)
			messages.success(request, f"Send pushies to {len(success)} / {len(results)} devices")

		return redirect("web_push:test")


@require_POST
@verified_account
def save_push_settings(request):
	form = PushSettingsForm(request.POST, instance=get_object_or_404(PushSettings, user=request.user))

	form.full_clean()
	if form.is_valid():
		form.save()
		messages.success(request, "Einstellungen erfolgreich gespeichert")
	else:
		messages.error(request, "Einstellungen konnten nicht gespeichert werden")

	return redirect("web_push:settings")


@require_POST
@verified_account
def register_webpush(request):
    data = json.loads(request.body)

    instance = WebPushDevice.objects.filter(registration_id=data["registration_id"]).first()
    form = RegisterWebPushDeviceForm(data, instance=instance)
    form.full_clean()
    if form.is_valid():
        object = form.save(commit=False)
        object.user = request.user
        object.save()

        return JsonResponse({"message": "success"})
    return JsonResponse({"message": "error"}, status=400)


@require_POST
@verified_account
def send_testmessage(request):
	PushSettings.send_message([request.user], "Test", "dies ist eine Test-Benachrichtiging, die du dir selbst geschickt hast.", PushTag.other)
	return JsonResponse({"message": "sent"})
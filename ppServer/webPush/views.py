import json

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http.request import HttpRequest as HttpRequest
from django.http.response import HttpResponse as HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST
from django.views.generic.base import TemplateView

from push_notifications.models import WebPushDevice

from ppServer.mixins import SpielleiterOnlyMixin
from ppServer.settings import PUSH_NOTIFICATION_KEY

from .forms import *


class TestView(SpielleiterOnlyMixin, TemplateView):
	template_name = "webPush/testpage.html"

	def get(self, request: HttpRequest) -> HttpResponse:
		return render(request, self.template_name, {"app_server_key": PUSH_NOTIFICATION_KEY})

	def post(self, request):
		message = request.POST.get("message") or "<default message>"
		print(message)

		results = WebPushDevice.objects.all().send_message(message)
		success = [r for r in results if "success" in r]
		error = [r for r in results if "failure" in r]
		print("Errors on send:", error)

		messages.success(request, f"Send pushies to {len(success)} / {WebPushDevice.objects.filter(active=True).count()} devices")
		return redirect("web_push:test")


@require_POST
@login_required
def register_webpush(request):
    data = json.loads(request.body)
    print(data)

    instance = WebPushDevice.objects.filter(registration_id=data["registration_id"]).first()
    form = RegisterWebPushDeviceForm(data, instance=instance)
    form.full_clean()
    if form.is_valid():
        object = form.save(commit=False)
        object.user = request.user
        object.save()

        return JsonResponse({"message": "success"})
    return JsonResponse({"message": "error"}, status=400)


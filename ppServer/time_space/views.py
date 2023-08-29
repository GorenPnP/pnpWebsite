import json
from typing import Any, Dict
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect, render, reverse
from django.views.generic import DetailView
from django.views.generic.base import TemplateView
from django.views.generic.list import ListView

from markdown_view.views import MarkdownView

from ppServer.mixins import SpielleiterOnlyMixin

from .models import *

class IndexView(LoginRequiredMixin, SpielleiterOnlyMixin, ListView):
	model = Level
	template_name = "time_space/index.html"

	def get_context_data(self, *args, **kwargs):
		return super().get_context_data(*args, **kwargs,
			topic = "Zeituhr",
			plus = "+ Netz",
			plus_url = reverse("time_space:createNet"),
		)


class PlayNetView(LoginRequiredMixin, SpielleiterOnlyMixin, DetailView):
	model = Level
	template_name = "time_space/net.html"

	def get_context_data(self, *args, **kwargs):
		context = super().get_context_data(*args, **kwargs)
		context["topic"] = context["object"].name
		context["app_index"] = "Zeituhr"
		context["app_index_url"] = reverse("time_space:index")

		return context


class EditNetView(LoginRequiredMixin, SpielleiterOnlyMixin, TemplateView):
	template_name = "time_space/editor.html"
	
	def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
		level = Level.objects.get(pk=self.kwargs["pk"]) if "pk" in self.kwargs else None
		return super().get_context_data(**kwargs,
			object = level,
			topic = level.name if level else "Neues Zeitproblem",
			app_index = "Zeituhr",
			app_index_url = reverse("time_space:index")
		)
	
	def post(self, request, *args, **kwargs):
		level_data = {
			"name": request.POST.get("levelName"),
			"width": int(request.POST.get("width")),
			"height": int(request.POST.get("height")),
			"tiles": json.loads(request.POST.get("tiles")),
		}

		id = self.kwargs["pk"] if "pk" in self.kwargs else None
		if id:
			level = Level.objects.filter(id=id).update(**level_data)
		else:
			level = Level.objects.create(**level_data)

		return redirect(reverse("time_space:editNet", args=[level.id]))


class ManualView(LoginRequiredMixin, SpielleiterOnlyMixin, MarkdownView):
	template_name = "time_space/manual.html"
	file_name='/static/time_space/manual.md'

	def get_context_data(self, *args, **kwargs):
		return super().get_context_data(*args, **kwargs,
			topic = "Manual",
			app_index = "Zeituhr",
			app_index_url = reverse("time_space:index"),
		)

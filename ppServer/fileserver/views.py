from typing import Any, Dict

from django.db.models import Q
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http.request import HttpRequest
from django.http.response import HttpResponse
from django.shortcuts import redirect
from django.urls import reverse
from django.views.generic import DetailView
from django.views.generic.base import TemplateView

from ppServer.mixins import VerifiedAccountMixin

from .models import Topic

class TopicListView(LoginRequiredMixin, VerifiedAccountMixin,  TemplateView):
    template_name = 'fileserver/maps.html'

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        return super().get_context_data(
            **kwargs,
            object_list=self.object_list,
            topic="Dateien",
            app_index="Wiki",
			app_index_url=reverse("wiki:index")
        )

    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        self.object_list = Topic.objects.filter(Q(sichtbarkeit_eingeschränkt=False) | Q(sichtbar_für__name=request.user.username)).distinct()
        return super().get(request, *args, **kwargs)


class TopicDetailView(LoginRequiredMixin, VerifiedAccountMixin,  DetailView):
    model = Topic
    template_name = 'fileserver/show_map.html'

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        # get rid of 'files/' prefix
        files = [{"name": m.file.name[m.file.name.find("/")+1:], "url": m.file.url} for m in self.object.files.all()]

        return super().get_context_data(**kwargs,
            topic=self.object.titel,
            files=files,
            app_index="Dateien",
			app_index_url=reverse("file:index")
        )

    def get(self, request: HttpRequest, pk: int, *args: Any, **kwargs: Any) -> HttpResponse:
        if Topic.objects.filter(~Q(sichtbar_für__name=request.user.username), pk=pk, sichtbarkeit_eingeschränkt=True).exists():
            return redirect("file:index")

        return super().get(request, *args, **kwargs)
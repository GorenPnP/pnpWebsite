from typing import Any, Dict

from django.db.models import Q
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse
from django.views.generic.list import ListView

from ppServer.mixins import VerifiedAccountMixin

from .models import Topic

class TopicListView(LoginRequiredMixin, VerifiedAccountMixin, ListView):
    model = Topic
    template_name = 'fileserver/index.html'

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        return super().get_context_data(
            **kwargs,
            topic="Dateien",
            app_index="Wiki",
			app_index_url=reverse("wiki:index")
        )
    
    def get_queryset(self):
        return self.model.objects.prefetch_related("files").filter(Q(sichtbarkeit_eingeschränkt=False) | Q(sichtbar_für=self.request.spieler.instance)).distinct()

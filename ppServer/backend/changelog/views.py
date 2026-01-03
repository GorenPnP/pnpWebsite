from typing import Any, Dict

from django.views.generic.list import ListView

from .models import Changelog

# Create your views here.
class ChangelogListView(ListView):

    model = Changelog
    template_name = "changelog/index.html"


    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        return super().get_context_data(**kwargs, topic = "Updates")


from django.contrib.admin.models import LogEntry
from django.contrib.auth.mixins import LoginRequiredMixin

from base.abstract_views import DynamicTableView, GenericTable
from ppServer.mixins import SpielleiterOnlyMixin

from .models import Log

class UserLogView(LoginRequiredMixin, SpielleiterOnlyMixin, DynamicTableView):
    model = Log
    filterset_fields = {
        "char": ["exact"],
        "spieler": ["exact"],
        "art": ["icontains"],
        "notizen": ["icontains"],
        "kosten": ["icontains"],
        "timestamp": ["lte"],
    }
    table_fields = ["char", "spieler", "art", "notizen", "kosten", "timestamp"]

    def get_app_index(self): return None
    def get_app_index_url(self): return None


class AdminLogView(LoginRequiredMixin, SpielleiterOnlyMixin, DynamicTableView):
    class Table(GenericTable):
        class Meta:
            model = LogEntry
            fields = ["action_time", "user", "object_repr", "change_message"]
            attrs= {"class": "table table-dark table-striped table-hover"}

        def render_change_message(self, value, record):
            return record.get_change_message()

    model = LogEntry
    queryset = LogEntry.objects.exclude(user__username="spielleiter").filter(content_type__app_label="character", content_type__model="charakter")
    
    topic = "Changes in Admin area"
    filterset_fields = {"action_time": ["lte"], "user": ["exact"], "object_repr": ["icontains"], "change_message": ["icontains"]}
    table_class = Table
    
    def get_app_index(self): return None
    def get_app_index_url(self): return None

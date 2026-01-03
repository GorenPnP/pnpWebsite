from typing import Any
from django.contrib import admin
from django.db.models.query import QuerySet
from django.http import HttpRequest

from .models import *


class ProposalInLineAdmin(admin.TabularInline):
    model = Proposal
    fields = ["order", "player", "start", "note"]
    readonly_fields = ["start", "note"]
    fk_name = "day"
    extra = 1

class AppointmentInLineAdmin(admin.TabularInline):
    model = Appointment
    fields = ["title", "tags", "start"]

class BlockedTimeInLineAdmin(admin.TabularInline):
    model = BlockedTime
    fields = ["name", "start", "end"]


class DayAdmin(admin.ModelAdmin):
    exclude = ["proposals", "appointment"]
    inlines = [BlockedTimeInLineAdmin, ProposalInLineAdmin, AppointmentInLineAdmin]

    def get_queryset(self, request: HttpRequest) -> QuerySet[Any]:
        return super().get_queryset(request).prefetch_related("blockedtime", "proposals")


admin.site.register(Tag)
admin.site.register(Day, DayAdmin)
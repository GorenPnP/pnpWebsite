from typing import Any
from django.contrib import admin
from django.db.models.query import QuerySet
from django.http import HttpRequest
from django.utils.html import format_html

from .models import *


class SpielerPageInlineAdmin(admin.TabularInline):
    model = SpielerPage
    fields = ["spieler", "answer"]
    readonly_fields = ["spieler", "answer"]
    extra = 0

    def has_add_permission(self, *args, **kwargs) -> bool:
        return False


class InquiryInlineAdmin(admin.TabularInline):
    model = Inquiry
    fields = ["spieler", "question", "response"]
    readonly_fields = ["spieler", "question"]
    extra = 0

    def has_add_permission(self, *args, **kwargs) -> bool:
        return False


class PageAdmin(admin.ModelAdmin):
    list_display = ["titel", "einheit", "number"]
    inlines = [SpielerPageInlineAdmin, InquiryInlineAdmin]

class PageImageAdmin(admin.ModelAdmin):
    list_display = ["_image", "page", "spielerPage"]
    list_filter = ["page", "spielerPage__spieler"]
    list_display_links = ["_image", "page"]

    def _image(self, obj):
        html = format_html('<img src="{0}" style="max-width: 32px; max-height:32px;" />'.format(obj.image.url))
        return html if html else self.get_empty_value_display()
    
    def get_queryset(self, request: HttpRequest) -> QuerySet[Any]:
        return super().get_queryset(request).prefetch_related("page__einheit", "spielerPage__page__einheit", "spielerPage__spieler")


admin.site.register(Fach)
admin.site.register(Einheit)
admin.site.register(Page, PageAdmin)
admin.site.register(PageImage, PageImageAdmin)

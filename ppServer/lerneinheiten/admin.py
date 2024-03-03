from django.contrib import admin

from .models import *

class InquiryAdmin(admin.ModelAdmin):
    list_display = ["question", "response", "spieler", "page"]
    list_filter = ["spieler", "page"]



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


admin.site.register(Fach)
admin.site.register(Einheit)
admin.site.register(Page, PageAdmin)
admin.site.register(Inquiry, InquiryAdmin)
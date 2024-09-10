from django.contrib import admin
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.html import format_html

from .models import *

class PoliticianInlineAdmin(admin.TabularInline):
    model = Politician
    fields = ["portrait", "name", "is_party_lead", "party", "genere", "birthyear"]
    extra = 3
    verbose_name = Politician._meta.verbose_name
    verbose_name_plural = Politician._meta.verbose_name_plural

class PartyAdmin(admin.ModelAdmin):
    fields = ["color", "name", "abbreviation", "description", "rightwing_tendency"]

    list_display = ["_color", "name", "abbreviation", "rightwing_tendency"]
    list_display_links = ["name"]

    inlines = [PoliticianInlineAdmin]

    def _color(self, obj):
        if not obj.color: return self.get_empty_value_display()
        return format_html(f'<div style="width: 32px; aspect-ratio:1; border-radius: 100%; background-color:{obj.color}" />')


class PoliticianAdmin(admin.ModelAdmin):
    fields = ["portrait", "name", "is_party_lead", "party", "genere", "birthyear"]

    list_display = ["_portrait", "name", "is_party_lead", "party", "genere", "birthyear"]
    list_display_links = ["name"]
    actions = ["duplicate_selected"]
    list_filter = ["party", "is_party_lead"]

    def _portrait(self, obj):
        if not obj.portrait or not obj.portrait.url: return self.get_empty_value_display()
        return format_html('<img src="{0}" style="max-width: 32px; max-height:32px;" />'.format(obj.portrait.url))

    @admin.action(description="Ausgewählte duplizieren")
    def duplicate_selected(self, request, queryset):
        selected = queryset.values_list("pk", flat=True)
        return HttpResponseRedirect(reverse("politics:admin-duplicate-politicians") + f"?ids={','.join(str(pk) for pk in selected)}")


admin.site.register(Party, PartyAdmin)
admin.site.register(Politician, PoliticianAdmin)
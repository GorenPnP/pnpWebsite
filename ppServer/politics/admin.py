from django.contrib import admin
from django.http import HttpResponseRedirect, HttpRequest
from django.urls import reverse
from django.utils.html import format_html

from markdownfield.widgets import MDEAdminWidget

from .models import *

class PoliticianInlineAdmin(admin.TabularInline):
    model = Politician
    fields = ["portrait", "name", "is_party_lead", "party", "genere", "birthyear"]
    extra = 3
    verbose_name = Politician._meta.verbose_name
    verbose_name_plural = Politician._meta.verbose_name_plural

class PartyAdmin(admin.ModelAdmin):
    fields = ["color", "textColor", "name", "abbreviation", "program", "leftwing_tendency"]

    list_display = ["_logo", "name", "leftwing_tendency"]
    list_display_links = ["_logo", "name"]

    inlines = [PoliticianInlineAdmin]

    def _logo(self, obj):
        if not obj.color: return obj.name or self.get_empty_value_display()
        
        style = f"background-color:{obj.color}; color:{obj.textColor}; padding: .3em .5em; line-height: 1em; font-size: 1.2rem;"
        return format_html(f'<div style="{style}"><b>{obj.abbreviation}</b></div>')

    @admin.display(ordering="text_rendered")
    def _program(self, obj):
        return format_html(obj.program_rendered)
    
        # use md-editor for a(ll) TextFields
    formfield_overrides = {
        "program": {"widget": MDEAdminWidget(options={
        "spellChecker": False,
        "toolbar": [
            "undo", "redo", "|",
            "bold", "italic", "heading-1", "heading-2", "heading-3", "|",
            "unordered-list", "ordered-list", "table", "|",
            "link", "quote", "|",
            "guide"
        ]
        })},
    }

class PoliticianAdmin(admin.ModelAdmin):
    fields = ["portrait", "name", "is_party_lead", "party", "member_of_parliament", "genere", "birthyear"]

    list_display = ["_portrait", "name", "is_party_lead", "party", "member_of_parliament", "genere", "birthyear"]
    list_display_links = ["name"]
    actions = ["duplicate_selected"]
    list_filter = ["party", "is_party_lead"]

    def _portrait(self, obj):
        if not obj.portrait or not obj.portrait.url: return self.get_empty_value_display()
        return format_html('<img src="{0}" style="max-width: 32px; max-height:32px;" loading="lazy" />'.format(obj.portrait.url))

    @admin.action(description="Ausgewählte duplizieren")
    def duplicate_selected(self, request, queryset):
        selected = queryset.values_list("pk", flat=True)
        return HttpResponseRedirect(reverse("politics:admin-duplicate-politicians") + f"?ids={','.join(str(pk) for pk in selected)}")


class LegalActAdmin(admin.ModelAdmin):
    """ uses 'politics:admin-vote-on-legalAct' as detail/update view, see ppServer/urls.py """
    class Media:
        css = {
            "all": ["res/css/easyMDE.css"],
        }

    fields = ["code", "paragraph", "text", "voting_done"]
    list_display = ["code", "paragraph", "_text", "voting_done"]
    list_display_links = []

    def _text(self, obj):
        return format_html(obj.text_rendered) if obj.text else self.get_empty_value_display()

    # use md-editor for a(ll) TextFields
    formfield_overrides = {
        models.TextField: {"widget": MDEAdminWidget(options={
        "spellChecker": False,
        "toolbar": [
            "undo", "redo", "|",
            "bold", "italic", "heading-1", "heading-2", "heading-3", "|",
            "unordered-list", "ordered-list", "table", "|",
            "link", "quote", "|",
            "guide"
        ]
        })},
    }

    
    def has_module_permission(self, request: HttpRequest) -> bool:
        return request.spieler.is_spielleitung


admin.site.register(Party, PartyAdmin)
admin.site.register(Politician, PoliticianAdmin)
admin.site.register(LegalAct, LegalActAdmin)
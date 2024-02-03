from django.contrib import admin
from django.http.request import HttpRequest

from markdownfield.widgets import MDEAdminWidget

from .models import *

class RuleAdmin(admin.ModelAdmin):
    class Media:
        css = {
            "all": ["wiki/css/md_editor.css"],
        }

    list_display = ["nr", "titel"]
    list_editable = ["nr"]
    list_display_links = ["titel"]

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
        return request.user.groups.filter(name__iexact="spielleiter").exists()


admin.site.register(Rule, RuleAdmin)

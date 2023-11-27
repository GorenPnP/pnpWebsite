from django.contrib import admin
from django.utils.html import format_html

from .models import *


class MonsterFormsInLineAdmin(admin.TabularInline):
    verbose_name = "andere Form"
    verbose_name_plural = "andere Formen"

    model = Monster.forms.through    
    fk_name = "from_monster"
    extra = 1
class GegenmonsterInLineAdmin(admin.TabularInline):
    verbose_name = "Gegenmonster"
    verbose_name_plural = "Gegenmonster"

    model = Monster.opposite.through    
    fk_name = "from_monster"
    extra = 1

class AttackeInLineAdmin(admin.TabularInline):
    verbose_name = "Attacke"
    verbose_name_plural = "Attacken"

    model = Monster.attacken.through
    extra = 1

class MonsterAdmin(admin.ModelAdmin):

    fieldsets = [
        ("Basics", {'fields': ['number', "name", "types"]}),
        ("Aussehen", {'fields': ['image', 'height', "weight", "description", "habitat"]}),
        ('Start-Werte', {'fields': ['wildrang', 'base_hp', "base_schadensWI"]}),
        ('Evolution', {'fields': ['evolutionPre', 'evolutionPost']}),
    ]

    inlines = [MonsterFormsInLineAdmin, GegenmonsterInLineAdmin, AttackeInLineAdmin]

    list_display = ['image_', 'number', 'name', 'types_', 'description']

    list_filter = ['base_hp', 'base_schadensWI']
    search_fields = ['number', 'name', 'description']
    list_display_links = ["name"]


    def image_(self, obj):
        return format_html(f"<img src='{obj.image.url}' style='max-width: 32px; max-height:32px;'>") if obj.image else "-"
    def types_(self, obj):
        return ", ".join([t.__str__() for t in obj.types.all()]) or "-"


class TypAdmin(admin.ModelAdmin):

    list_display = ['image_', 'name']

    list_filter = ['name']
    search_fields = ['name']
    list_display_links = ["name"]

    def image_(self, obj):
        return format_html(f"<img src='{obj.icon.url}' style='max-width: 32px; max-height:32px;'>") if obj.icon else "-"


class AttackeAdmin(admin.ModelAdmin):

    list_display = ['name', 'types_', 'description', 'macht_schaden', 'macht_effekt']

    list_filter = ['name', "types", "macht_schaden", "macht_effekt"]
    search_fields = ['name', "description"]
    list_display_links = ["name"]
    list_editable = ["macht_schaden", "macht_effekt"]

    def types_(self, obj):
        return ", ".join([t.__str__() for t in obj.types.all()]) or "-"




admin.site.register(Typ, TypAdmin)
admin.site.register(Monster, MonsterAdmin)
admin.site.register(Attacke, AttackeAdmin)
admin.site.register(Dice)
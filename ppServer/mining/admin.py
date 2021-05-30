from django.contrib import admin
from django.utils.html import format_html

from .models import *


class MaterialDropInLineAdmin(admin.TabularInline):
    model = MaterialDrop
    extra = 1


class MaterialInLineAdmin(admin.TabularInline):
    model = Material
    extra = 1


class LayerInLineAdmin(admin.TabularInline):
    model = Layer
    extra = 1

class EntityInLineAdmin(admin.TabularInline):
    model = Entity
    extra = 1


class MaterialAdmin(admin.ModelAdmin):
    list_display = ('_icon', 'name', 'rigidity', '_drops')
    list_display_links = ('_icon', 'name')
    search_fields = ('name',)

    inlines = [MaterialDropInLineAdmin]

    def _icon(self, obj):
        html = format_html('<img src="{0}" style="max-width: 32px; max-height:32px;" />'.format(obj.icon.url))
        return html if html else "-"

    def _drops(self, obj):
        html = ", ".join([drop.item.name for drop in MaterialDrop.objects.filter(material=obj)])
        return html if html else "-"


class RegionAdmin(admin.ModelAdmin):

    # auto-add layers on load
    class Media:
        js = ('mining/js/admin_region_create.js',)

    list_display = ('name',)

    inlines = [LayerInLineAdmin]

class MaterialGroupAdmin(admin.ModelAdmin):
    list_display = ('name', '_materials')

    def _materials(self, obj):
        return format_html("".join(['<img src="{0}" style="max-width: 32px; max-height:32px;" />'.format(m.icon.url) for m in obj.materials.all()]))


class LayerAdmin(admin.ModelAdmin):
    list_display = ('region', 'index')

    inlines = [EntityInLineAdmin]


class CraftingOriginatedMaterialAdmin(admin.ModelAdmin):
    list_display = ('item', 'material', 'is_collidable', 'is_breakable')


admin.site.register(Material, MaterialAdmin)
admin.site.register(MaterialGroup, MaterialGroupAdmin)
admin.site.register(Region, RegionAdmin)
admin.site.register(Layer, LayerAdmin)
admin.site.register(CraftingOriginatedMaterial, CraftingOriginatedMaterialAdmin)
admin.site.register(ProfileEntity)
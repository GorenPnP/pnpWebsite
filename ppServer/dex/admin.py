from django.contrib import admin
from django.utils.html import format_html

from .models import *


class PflanzenImageInLineAdmin(admin.TabularInline):
    verbose_name = "Bild"
    verbose_name_plural = "Bilder"

    model = ParaPflanzenImage
    extra = 1

class PflanzenAdmin(admin.ModelAdmin):

    list_display = ["images_", 'name', 'generation', 'number', 'besonderheiten']
    list_filter = ["generation"]
    search_fields = ["name", "besonderheiten"]
    list_display_links = ["name"]
    
    exclude = ["images"]
    inlines = [PflanzenImageInLineAdmin]

    def images_(self, obj):
        pf_imgs = ParaPflanzenImage.objects.filter(plant=obj, is_vorschau=True)
        return format_html("".join([f"<img src='{pf_img.image.url}' style='max-width: 32px; max-height:32px;'>" for pf_img in pf_imgs]) or "-")


class TierFertigkeitInLineAdmin(admin.TabularInline):
    verbose_name = "Fertigkeit"
    verbose_name_plural = "Fertigkeiten"

    model = ParaTierFertigkeit
    extra = 1

class TierAdmin(admin.ModelAdmin):

    list_display = ["image_", 'name', 'description']
    search_fields = ["name", "description"]
    list_display_links = ["name"]

    inlines = [TierFertigkeitInLineAdmin]

    def image_(self, obj):
        return format_html(f"<img src='{obj.image.url}' style='max-width: 32px; max-height:32px;'>") if obj.image else "-"


class GeschöpfFertigkeitInLineAdmin(admin.TabularInline):
    verbose_name = "Fertigkeit"
    verbose_name_plural = "Fertigkeiten"

    model = GeschöpfFertigkeit
    extra = 1

class GeschöpfAdmin(admin.ModelAdmin):

    list_display = ["image_", 'name', 'klassierung', 'initiative', 'hp', 'schaWI_', 'reaktion', 'status']
    search_fields = ["name"]
    list_display_links = ["name"]

    inlines = [GeschöpfFertigkeitInLineAdmin]

    def image_(self, obj):
        return format_html(f"<img src='{obj.image.url}' style='max-width: 32px; max-height:32px;'>") if obj.image else "-"
    def klassierung(self, obj):
        return f"{obj.gefahrenklasse}{obj.verwahrungsklasse}"
    def schaWI_(self, obj):
        return "+".join([f"{t.amount}{t.type}" for t in obj.schaWI.all()]) or "-"


admin.site.register(Dice)
admin.site.register(Fertigkeit)
admin.site.register(ParaPflanze, PflanzenAdmin)
admin.site.register(ParaTier, TierAdmin)
admin.site.register(Geschöpf, GeschöpfAdmin)
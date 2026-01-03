from typing import Any
from django.contrib import admin
from django.db.models.query import QuerySet
from django.http import HttpRequest
from django.utils.html import format_html

from .models import *


class PflanzenImageInLineAdmin(admin.TabularInline):
    verbose_name = "Bild"
    verbose_name_plural = "Bilder"

    model = ParaPflanzenImage
    extra = 1
class PflanzenÖkologieInLineAdmin(admin.TabularInline):
    model = ParaPflanzeÖkologie
    extra = 1

class PflanzenAdmin(admin.ModelAdmin):

    list_display = ["images_", 'name', 'generation', 'number', 'besonderheiten']
    list_filter = ["generation"]
    search_fields = ["name", "besonderheiten"]
    list_display_links = ["name"]

    inlines = [PflanzenImageInLineAdmin, PflanzenÖkologieInLineAdmin]

    def images_(self, obj):
        pf_imgs = obj.parapflanzenimage_set.filter(is_vorschau=True)
        return format_html("".join([f"<img src='{pf_img.image.url}' style='max-width: 32px; max-height:32px;' loading='lazy'>" for pf_img in pf_imgs]) or self.get_empty_value_display())
    
    def get_queryset(self, request: HttpRequest) -> QuerySet[Any]:
        return super().get_queryset(request).prefetch_related("parapflanzenimage_set")


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
        return format_html(f"<img src='{obj.image.url}' style='max-width: 32px; max-height:32px;' loading='lazy'>") if obj.image else self.get_empty_value_display()


class GeschöpfFertigkeitInLineAdmin(admin.TabularInline):
    verbose_name = "Fertigkeit"
    verbose_name_plural = "Fertigkeiten"

    model = GeschöpfFertigkeit
    extra = 1

class GeschöpfAdmin(admin.ModelAdmin):

    list_display = ["image_", 'name', 'klassierung', 'initiative', 'hp', 'schadensWI_', 'reaktion', 'status']
    search_fields = ["name"]
    list_display_links = ["name"]

    inlines = [GeschöpfFertigkeitInLineAdmin]

    def image_(self, obj):
        return format_html(f"<img src='{obj.image.url}' style='max-width: 32px; max-height:32px;' loading='lazy'>") if obj.image else self.get_empty_value_display()
    def klassierung(self, obj):
        return f"{obj.gefahrenklasse}{obj.verwahrungsklasse}"
    def schadensWI_(self, obj):
        return "+".join([f"{t.amount}{t.type}" for t in obj.schadensWI.all()]) or self.get_empty_value_display()
    
    def get_queryset(self, request: HttpRequest) -> QuerySet[Any]:
        return super().get_queryset(request).prefetch_related("initiative", "schadensWI")


admin.site.register(Dice)
admin.site.register(Fertigkeit)
admin.site.register(ParaPflanze, PflanzenAdmin)
admin.site.register(ParaTier, TierAdmin)
admin.site.register(Geschöpf, GeschöpfAdmin)
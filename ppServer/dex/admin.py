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
class EvoliutionPreInLineAdmin(admin.TabularInline):
    verbose_name = "Vorentwicklung"
    verbose_name_plural = "Vorentwicklungen"

    model = Monster.evolutionPre.through    
    fk_name = "from_monster"
    extra = 1
class EvolutionPostInLineAdmin(admin.TabularInline):
    verbose_name = "Weiterentwicklung"
    verbose_name_plural = "Weiterentwicklungen"

    model = Monster.evolutionPost.through    
    fk_name = "from_monster"
    extra = 1

class AttackeInLineAdmin(admin.TabularInline):
    verbose_name = "Attacke"
    verbose_name_plural = "Attacken"

    model = Monster.attacken.through
    extra = 1

class MonsterAdmin(admin.ModelAdmin):
    change_list_template = "dex/admin/change_list_monster.html"

    fieldsets = [
        ("Basics", {'fields': ['number', "name", "types", "fähigkeiten", "visible"]}),
        ("Aussehen", {'fields': ['image', 'height', "weight", "description", "habitat"]}),
        ('Start-Werte', {'fields': ['wildrang', 'base_hp', "base_schadensWI", "base_attackbonus", "base_reaktionsbonus"]}),
    ]

    inlines = [MonsterFormsInLineAdmin, GegenmonsterInLineAdmin, EvoliutionPreInLineAdmin, EvolutionPostInLineAdmin, AttackeInLineAdmin]

    list_display = ['image_', 'number', 'name', 'types_', 'wildrang', 'base_hp', "base_schadensWI_", "base_attackbonus", "base_reaktionsbonus"]

    list_filter = ['base_hp', 'base_schadensWI']
    search_fields = ['number', 'name', 'description']
    list_display_links = ["name"]
    list_editable = ['wildrang', 'base_hp', "base_attackbonus", "base_reaktionsbonus"]


    def image_(self, obj):
        return format_html(f"<img src='{obj.image.url}' style='max-width: 32px; max-height:32px;'>") if obj.image else "-"
    def types_(self, obj):
        return format_html("".join([t.tag() for t in obj.types.all()])) or "-"
    def base_schadensWI_(self, obj):
        return " + ".join([t.__str__() for t in obj.base_schadensWI.all()]) or "-"


class MonsterFähigkeitAdmin(admin.ModelAdmin):
    list_display = ["name", "description"]
    search_fields = ["name", "description"]


class MonsterRangAdmin(admin.ModelAdmin):
    list_display = ["rang", "hp", "schadensWI_", "reaktionsbonus", "angriffsbonus"]
    list_editable = ["hp", "reaktionsbonus", "angriffsbonus"]

    def schadensWI_(self, obj):
        return " + ".join([t.__str__() for t in obj.schadensWI.all()]) or "-"

class TypAdmin(admin.ModelAdmin):

    list_display = ['Aussehen_', "stark_gegen_", "schwach_gegen_", "trifft_nicht_"]

    list_filter = ['name', "stark_gegen", "schwach_gegen", "trifft_nicht"]
    search_fields = ['name']

    def stark_gegen_(self, obj):
        return format_html("".join([t.tag() for t in obj.stark_gegen.all()])) or "-"
    def schwach_gegen_(self, obj):
        return format_html("".join([t.tag() for t in obj.schwach_gegen.all()])) or "-"
    def trifft_nicht_(self, obj):
        return format_html("".join([t.tag() for t in obj.trifft_nicht.all()])) or "-"
    def Aussehen_(self, obj):
        return obj.tag()


class AttackeAdmin(admin.ModelAdmin):

    list_display = ['name', 'types_', 'description', 'damage_', 'macht_schaden', 'macht_effekt']

    list_filter = ["types", "macht_schaden", "macht_effekt"]
    search_fields = ['name', "description"]
    list_display_links = ["name"]
    list_editable = ["macht_schaden", "macht_effekt"]

    def damage_(self, obj):
        return " + ".join([t.__str__() for t in obj.damage.all()]) or "-"
    def types_(self, obj):
        return ", ".join([t.__str__() for t in obj.types.all()]) or "-"


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

    list_display = ["image_", 'name', 'hp', 'schaWI_', 'reaktion', 'status']
    search_fields = ["name"]
    list_display_links = ["name"]

    inlines = [GeschöpfFertigkeitInLineAdmin]

    def image_(self, obj):
        return format_html(f"<img src='{obj.image.url}' style='max-width: 32px; max-height:32px;'>") if obj.image else "-"
    def schaWI_(self, obj):
        return "+".join([f"{t.amount}{t.type}" for t in obj.schaWI.all()]) or "-"



admin.site.register(Typ, TypAdmin)
admin.site.register(Monster, MonsterAdmin)
admin.site.register(Attacke, AttackeAdmin)
admin.site.register(Dice)
admin.site.register(Fertigkeit)
admin.site.register(MonsterRang, MonsterRangAdmin)
admin.site.register(MonsterFähigkeit, MonsterFähigkeitAdmin)
admin.site.register(ParaPflanze, PflanzenAdmin)
admin.site.register(ParaTier, TierAdmin)
admin.site.register(Geschöpf, GeschöpfAdmin)
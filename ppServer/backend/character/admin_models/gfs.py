from typing import Any
from django.contrib import admin
from django.db.models import OuterRef
from django.db.models.query import QuerySet
from django.http import HttpRequest
from django.utils.html import format_html

from ppServer.utils import get_filter, ConcatSubquery

from ..models import *


class GfsEigenschaftInLine(admin.TabularInline):
    model = Gfs.eigenschaften.through
    extra = 1

class GfsImageInLine(admin.TabularInline):
    model = GfsImage
    fields = ["order", "img", "text"]
    extra = 1

class GfsAttributInLine(admin.TabularInline):
    model = GfsAttribut
    fields = ["attribut", "aktuellerWert", "maxWert"]
    readonly_fields = ["attribut"]
    extra = 0

    def has_add_permission(self, request, obj=None):
        return False

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('attribut')


class GfsFertigkeitInLine(admin.TabularInline):
    model = GfsFertigkeit
    fields = ["fertigkeit", "fp"]
    readonly_fields = ["fertigkeit"]
    extra = 0

    def has_add_permission(self, request, obj=None):
        return False

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('fertigkeit', 'gfs')


class GfsVorteilInLine(admin.TabularInline):
    model = GfsVorteil
    extra = 1


class GfsNachteilInLine(admin.TabularInline):
    model = GfsNachteil
    extra = 1


class GfsWesenkraftInLine(admin.TabularInline):
    model = GfsWesenkraft
    extra = 1

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related("wesenkraft", "gfs")


class GfsZauberInLine(admin.TabularInline):
    model = GfsZauber
    extra = 1


class GfsSkilltreeInLine(admin.TabularInline):
    model = GfsSkilltreeEntry
    fields = ["base", "operation", "amount", "stufe", "text", "fertigkeit", "vorteil", "nachteil", "wesenkraft", "spezialfertigkeit", "wissensfertigkeit", "magische_ausrüstung"]
    extra = 1

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related("base", "gfs", "wesenkraft", "magische_ausrüstung", "vorteil", "nachteil",
            "spezialfertigkeit__attr1", "spezialfertigkeit__attr2", "wissensfertigkeit__attr1", "wissensfertigkeit__attr2", "wissensfertigkeit__attr3")

    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj, **kwargs)

        formset.form.base_fields["spezialfertigkeit"].queryset = formset.form.base_fields["spezialfertigkeit"].queryset.prefetch_related("attr1", "attr2")
        formset.form.base_fields["wissensfertigkeit"].queryset = formset.form.base_fields["wissensfertigkeit"].queryset.prefetch_related("attr1", "attr2", "attr3")

        return formset


class GfsStufenplanInLine(admin.TabularInline):
    model = GfsStufenplan
    fields = ["basis", "vorteile", "zauber", "wesenkräfte", "ability"]
    extra = 0

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('basis', 'vorteile', 'wesenkräfte', 'ability')



class GfsAdmin(admin.ModelAdmin):
    list_display = ('icon_', 'titel', 'ap', 'difficulty', 'vorteil_', 'nachteil_', 'zauber_',
                    "wesenschaden_waff_kampf", "wesenschaden_andere_gestalt", "wesenkraft_", "startmanifest",)
    list_filter = ["wesen", 'ap', 'startmanifest', "wesenschaden_waff_kampf"]
    search_fields = ('titel', 'ap')

    list_display_links = ["icon_", "titel"]

    fields = ["icon", "titel", "wesen", "beschreibung", "eigenschaften", "ap", "wesenschaden_waff_kampf", "wesenschaden_andere_gestalt", "startmanifest", "difficulty"]
    inlines = [GfsImageInLine, GfsAttributInLine, GfsFertigkeitInLine,
               GfsVorteilInLine, GfsNachteilInLine,
               GfsWesenkraftInLine, GfsZauberInLine,
               GfsSkilltreeInLine, GfsStufenplanInLine]
    
    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related("wesen").annotate(
            eigenschaftnames = ConcatSubquery(GfsEigenschaft.objects.filter(gfs=OuterRef("id")).values("name"), ", "),
            vorteilnames = ConcatSubquery(Vorteil.objects.filter(gfs=OuterRef("id")).values("titel"), ", "),
            nachteilnames = ConcatSubquery(Nachteil.objects.filter(gfs=OuterRef("id")).values("titel"), ", "),
            zaubernames = ConcatSubquery(GfsZauber.objects.prefetch_related("item").filter(gfs=OuterRef("id")).values("item__name"), ", "),
            wesenkraftnames = ConcatSubquery(Wesenkraft.objects.filter(gfs=OuterRef("id")).values("titel"), ", "),
        )

    def icon_(self, obj):
        return format_html(f'<img src="{obj.icon.url}" style="max-width: 32px; max-height:32px;" loading="lazy" />' if obj.icon else self.get_empty_value_display())

    @admin.display(ordering="eigenschaftnames")
    def eigenschaft_(self, obj):
        return obj.eigenschaftnames or self.get_empty_value_display()

    @admin.display(ordering="vorteilnames")
    def vorteil_(self, obj):
        return obj.vorteilnames or self.get_empty_value_display()

    @admin.display(ordering="nachteilnames")
    def nachteil_(self, obj):
        return obj.nachteilnames or self.get_empty_value_display()

    @admin.display(ordering="zaubernames")
    def zauber_(self, obj):
        return obj.zaubernames or self.get_empty_value_display()

    @admin.display(ordering="wesenkraftnames")
    def wesenkraft_(self, obj):
        return obj.wesenkraftnames or self.get_empty_value_display()

    def _beschreibung(self, obj):
        return format_html(obj.beschreibung_rendered)




class GfsStufenplanBaseAdmin(admin.ModelAdmin):
    list_display = ["stufe", "ep", "ap", "fp", "fg", "tp"]
    list_editable = ["ep", "ap", "fp", "fg", "tp"]

class GfsStufenplanAdmin(admin.ModelAdmin):
    list_display = ["stufe", "gfs", "_vorteile", "_wesenkräfte", "zauber", "ability"]
    list_filter = ["basis__stufe", "gfs"]

    @admin.display(ordering="basis__stufe")
    def stufe(self, obj):
        return obj.basis.stufe
    def _vorteile(self, obj):
        return ",".join([e.__str__() for e in obj.vorteile.all()]) or self.get_empty_value_display()
    def _wesenkräfte(self, obj):
        return ",".join([e.__str__() for e in obj.wesenkräfte.all()]) or self.get_empty_value_display()


class GfsAbilityAdmin(admin.ModelAdmin):
    list_display = ("name", "beschreibung", "_gfs", "_stufe", "needs_implementation", "has_implementation", "has_choice")
    list_editable = ["beschreibung", "needs_implementation", "has_implementation", "has_choice"]

    list_filter = [get_filter(Gfs, "titel", ["gfsstufenplan__gfs__titel"]), "needs_implementation", "has_choice"]
    search_fields = ("name", "beschreibung__contains")

    @admin.display(ordering="gfsstufenplan__gfs__titel")
    def _gfs(self, obj):
        return obj.gfsstufenplan.gfs.titel

    @admin.display(ordering="gfsstufenplan__basis__stufe")
    def _stufe(self, obj):
        return obj.gfsstufenplan.basis.stufe
    
    def get_queryset(self, request: HttpRequest) -> QuerySet[Any]:
        return super().get_queryset(request).prefetch_related("gfsstufenplan__gfs", "gfsstufenplan__basis")


class GfsEigenschaftAdmin(admin.ModelAdmin):
    list_display = ('name', 'beschreibung', '_gfs')

    inlines = [GfsEigenschaftInLine]

    @admin.display(ordering="gfsnames")
    def _gfs(self, obj):
        return obj.gfsnames or self.get_empty_value_display()
    
    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            gfsnames = ConcatSubquery(Gfs.objects.filter(eigenschaften=OuterRef("id")).values("titel"), ", "),
        )

    
class GfsSkilltreeEntryAdmin(admin.ModelAdmin):
    class IsCorrectlyFormattedFilter(admin.SimpleListFilter):
        title = 'correctly_formatted'
        parameter_name = 'correctly_formatted'

        def lookups(self, request, model_admin):
            return (
                ("y", "Korrekt"),
                ("n", "Falsch"),
            )

        def queryset(self, request, queryset):
            if self.value() is None: return queryset
            value = self.value() == "y"

            ids = []
            for e in queryset:
                is_correct = "error" not in e.__repr__().lower()
                if (value and is_correct) or (not value and not is_correct): ids.append(e.id)

            return queryset.filter(id__in=ids)

    list_display = ["context_", "entry", "operation", "correctly_formatted"]

    search_fields = ["gfs__titel", "base__stufe", "text__contains", "vorteil__titel", "nachteil__titel", "spezialfertigkeit__titel", "wissensfertigkeit__titel", "amount", "stufe", "wesenkraft__titel"]
    list_filter = [get_filter(Gfs, "titel", ["gfs__titel"]), "base__stufe", "operation", IsCorrectlyFormattedFilter]

    def context_(self, obj):
        return f"{obj.gfs.titel} St. {obj.base.stufe}"

    def entry(self, obj):
        return obj.__repr__()
    
    def correctly_formatted(self, obj):
        return "error" not in obj.__repr__().lower()
    correctly_formatted.boolean = True

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related(
            'gfs', 'base', 'fertigkeit', 'vorteil', 'nachteil', 'wesenkraft', 'spezialfertigkeit', 'wissensfertigkeit', 'magische_ausrüstung'
        )

from django.contrib import admin

from .models import *


class EffectAdmin(admin.ModelAdmin):
    list_display = ["target_fieldname", "wert", "has_custom_implementation", "target", "source"]
    list_filter = ["has_custom_implementation", "target_fieldname", "target_attribut", "target_fertigkeit",
    ]
    search_fields = [
        "target_fieldname",
        "target_attribut__titel",
        "target_fertigkeit__titel",
        
        "source_vorteil__titel",
        "source_nachteil__titel",
        "source_talent__titel",
        "source_gfsAbility__name",
        "source_klasse__titel",
        "source_klasseAbility__name",
        "source_shopBegleiter__name",
        "source_shopMagischeAusrüstung__name",
        "source_shopRüstung__name",
        "source_shopAusrüstungTechnik__name",
        "source_shopEinbauten__name",
    ]

    def wert(self, obj):
        return obj.wertaenderung_str or obj.wertaenderung

    def target(self, obj):
        targets = [getattr(obj, "target_attribut", None), getattr(obj, "target_fertigkeit", None)]
        return [t.__str__() for t in targets if t] or self.get_empty_value_display()

    def source(self, obj):
        return [getattr(obj, field.replace("_id", "")).__str__() for field, val in obj.__dict__.items() if "source_" in field and val]


admin.site.register(Effect, EffectAdmin)
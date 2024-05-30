from django.contrib import admin

from .models import *


class EffectAdmin(admin.ModelAdmin):
    list_display = ["target_fieldname", "wertaenderung", "has_custom_implementation", "target", "source"]
    list_filter = ["has_custom_implementation", "target_fieldname", "target_attribut", "target_fertigkeit",
    ]
    search_fields = [
        "target_fieldname", "target_attribut", "target_fertigkeit",
        "source_vorteil", "source_nachteil", "source_talent", "source_gfsAbility", "source_shopBegleiter", "source_shopMagischeAusrüstung", "source_shopRüstung", "source_shopAusrüstungTechnik", "source_shopEinbauten",
    ]

    def target(self, obj):
        targets = [getattr(obj, "target_attribut", None), getattr(obj, "target_fertigkeit", None)]
        return [t.__str__() for t in targets if t] or self.get_empty_value_display()

    def source(self, obj):
        return [getattr(obj, field.replace("_id", "")).__str__() for field, val in obj.__dict__.items() if "source_" in field and val]


admin.site.register(Effect, EffectAdmin)
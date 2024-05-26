from django.contrib import admin

from .models import *


class EffectAdmin(admin.ModelAdmin):
    list_display = ["target_fieldname", "wertaenderung", "has_custom_implementation", "target", "source"]

    def target(self, obj):
        targets = [getattr(obj, "target_attribut", None), getattr(obj, "target_fertigkeit", None)]
        return [t.__str__() for t in targets if t] or self.get_empty_value_display()

    def source(self, obj):
        return [getattr(obj, field.replace("_id", "")).__str__() for field, val in obj.__dict__.items() if "source_" in field and val]

class RelEffectAdmin(EffectAdmin):
    list_display = ["target_fieldname", "wertaenderung", "target", "source", "is_active"]

admin.site.register(Effect, EffectAdmin)
admin.site.register(RelEffect, RelEffectAdmin)
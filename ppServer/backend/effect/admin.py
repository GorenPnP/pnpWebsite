from django.contrib import admin

from character.models.char import Charakter

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
        "source_shopEinbaute__name",
    ]

    def wert(self, obj):
        return obj.wert

    def target(self, obj):
        targets = [getattr(obj, "target_attribut", None), getattr(obj, "target_fertigkeit", None)]
        return [t.__str__() for t in targets if t] or self.get_empty_value_display()

    def source(self, obj):
        return obj.source

    def get_readonly_fields(self, request, obj=None):
        if obj: # all source_ readonly if editing an existing object
            fields = [*self.readonly_fields, *[field.replace('_id', '') for field in obj.__dict__.keys() if 'source_' in field]]
            return fields
        return self.readonly_fields

    def save_model(self, request, obj, form, change):
        # add RelEffects on create of Effect
        if not change:
            super().save_model(request, obj, form, change)
            source_fieldname, source_obj = [(field.replace('_id', ''), getattr(obj, field.replace('_id', ''))) for field, val in obj.__dict__.items() if 'source_' in field and val][0]

            # gather chars
            chars = []
            if source_fieldname == "source_vorteil": chars = Charakter.objects.filter(relvorteil__teil=source_obj)
            if source_fieldname == "source_nachteil": chars = Charakter.objects.filter(relnachteil__teil=source_obj)
            if source_fieldname == "source_talent": chars = Charakter.objects.filter(reltalent__talent=source_obj)
            if source_fieldname == "source_gfsAbility": chars = Charakter.objects.filter(relgfsability__ability=source_obj)
            if source_fieldname == "source_klasseAbility": chars = Charakter.objects.filter(relklasseability__ability=source_obj)
            if source_fieldname == "source_klasse": chars = Charakter.objects.filter(relklasse__klasse=source_obj)
            if source_fieldname == "source_shopBegleiter": chars = Charakter.objects.filter(relbegleiter__item=source_obj)
            if source_fieldname == "source_shopMagischeAusrüstung": chars = Charakter.objects.filter(relmagische_ausrüstung__item=source_obj)
            if source_fieldname == "source_shopRüstung": chars = Charakter.objects.filter(relrüstung__item=source_obj)
            if source_fieldname == "source_shopEinbaute": chars = Charakter.objects.filter(releinbaute__item=source_obj)

            # create RelEffects for chars by calling them individually for signals to fire
            for char in chars: RelEffect.objects.create(effect=obj, target_char=char)

            return


        # get old and new data
        old_instance = Effect.objects.filter(pk=obj.pk).first() if change else None
        new_data = {k: v for k, v in form.cleaned_data.items() if k in ["wertaenderung", "wertaenderung_str", "target_fieldname", "target_attribut", "target_fertigkeit", "has_custom_implementation"]}

        # changes occurred?
        changes = [field for field, val in new_data.items() if getattr(old_instance, field) != val]
        if not changes: return super().save_model(request, obj, form, change)

        rel_pks = [*RelEffect.objects.filter(effect__pk=obj.pk, is_active=True).values_list("pk", flat=True)]

        # apply changes and populate them to RelEffects. save each RelEffect separately to trigger their Signals to de/activate
        for rel in RelEffect.objects.filter(pk__in=rel_pks):
            rel.is_active = False
            rel.save(update_fields=["is_active"])

        super().save_model(request, obj, form, change)

        for rel in RelEffect.objects.filter(pk__in=rel_pks):
            rel.is_active = True
            rel.save(update_fields=["is_active"])



admin.site.register(Effect, EffectAdmin)
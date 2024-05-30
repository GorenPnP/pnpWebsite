from django.db.models import Q, Value
from django.shortcuts import redirect
from django.views.generic import DetailView
from django.urls import path

import django_tables2 as tables

from base.abstract_views import GenericTable
from character.models import *
from ppServer.mixins import VerifiedAccountMixin, SpielleiterOnlyMixin

from .models import Effect
from .signals import apply_effect_on_rel_relation


# views
class SetReleffectsDetailView(VerifiedAccountMixin, SpielleiterOnlyMixin, tables.SingleTableMixin, DetailView):

    class Table(GenericTable):

        class Meta:
            attrs = GenericTable.Meta.attrs
            model = Effect
            fields = ["wertaenderung", "target_fieldname", "target", "source"]

        def render_target(self, value, record):
            targets = [getattr(record, "target_attribut", None), getattr(record, "target_fertigkeit", None)]
            return ", ".join([t.__str__() for t in targets if t]) or "-"

        def render_source(self, value, record):
            return ", ".join([getattr(record, field.replace("_id", "")).__str__() for field, val in record.__dict__.items() if "source_" in field and val])

    model = Charakter
    template_name = "effect/set_releffect_detail.html"

    table_class = Table
    table_pagination = False
    
    def get_context_data(self, *args, **kwargs):
        return super().get_context_data(*args, **kwargs,
            topic = self.object,
            table = self.Table(self.get_table_data()),
        )

    def get_table_data(self):
        char = self.object
        return Effect.objects.filter(
                Q(source_vorteil__in=char.vorteile.all()) |
                Q(source_nachteil__in=char.nachteile.all()) |
                Q(source_talent__in=char.talente.all()) |
                Q(source_gfsAbility__in=char.gfs_fähigkeiten.all()) |
                Q(source_shopBegleiter__in=char.begleiter.all()) |
                Q(source_shopMagischeAusrüstung__in=char.magischeAusrüstung.all()) |
                Q(source_shopRüstung__in=char.rüstungen.all()) |
                Q(source_shopAusrüstungTechnik__in=char.ausrüstungTechnik.all()) |
                Q(source_shopEinbauten__in=char.einbauten.all())
            ).annotate(
                target = Value("-"),
                source = Value("-"),
            )

    def post(self, *args, **kwargs):
        char = self.get_object()
        curr = char.releffect_set.count()
        max = Effect.objects.filter(
            Q(source_vorteil__in=char.vorteile.all()) |
            Q(source_nachteil__in=char.nachteile.all()) |
            Q(source_talent__in=char.talente.all()) |
            Q(source_gfsAbility__in=char.gfs_fähigkeiten.all()) |
            Q(source_shopBegleiter__in=char.begleiter.all()) |
            Q(source_shopMagischeAusrüstung__in=char.magischeAusrüstung.all()) |
            Q(source_shopRüstung__in=char.rüstungen.all()) |
            Q(source_shopAusrüstungTechnik__in=char.ausrüstungTechnik.all()) |
            Q(source_shopEinbauten__in=char.einbauten.all())
        ).count()
        
        if curr != max:
            char.releffect_set.all().delete()
            source_models = [
                RelVorteil,
                RelNachteil,
                RelTalent,
                RelGfsAbility,
                RelBegleiter,
                RelMagische_Ausrüstung,
                RelRüstung,
                RelAusrüstung_Technik,
                RelEinbauten
            ]
            for model in source_models:
                for rel_obj in model.objects.filter(char=char):
                    
                    apply_effect_on_rel_relation(model, rel_obj, True)
            
            
        return redirect("admin:character_charakter_changelist")



# urls

app_name = 'effect'

urlpatterns = [
    path('<int:pk>', SetReleffectsDetailView.as_view(), name='index'),
]

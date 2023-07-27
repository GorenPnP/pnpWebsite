from django.contrib import messages
from django.shortcuts import redirect
from django.views.generic.base import TemplateView
from django.utils.decorators import method_decorator
from django.utils.html import format_html

import django_tables2 as tables

from base.abstract_views import GenericTable
from character.models import GfsAbility, RelGfsAbility

from ..decorators import is_erstellung_done
from ..mixins import LevelUpMixin


@method_decorator([is_erstellung_done], name="dispatch")
class GenericGfsAbilityView(LevelUpMixin, tables.SingleTableMixin, TemplateView):

    class Table(GenericTable):

        class Meta:
            attrs = GenericTable.Meta.attrs
            model = GfsAbility
            fields = ["name", "beschreibung", "notiz"]

        notiz = tables.Column(verbose_name="Notizen")

        def render_notiz(self, value, record):
            return format_html(f"<textarea form='form' name='{record['id']}' required>{record['notizen']}</textarea>")


    template_name = "levelUp/gfs_ability.html"
    topic = "Gfs-Fähigkeiten"
    model = GfsAbility

    table_class = Table
    table_pagination = False

    def get_queryset(self):
        char = self.get_character()

        return [{"id": entry.id, "name": entry.ability.name, "beschreibung": entry.ability.beschreibung, "notizen": entry.notizen if entry.notizen else "", "notiz": "---" if entry.ability.has_choice else None} for entry in RelGfsAbility.objects.prefetch_related("ability").filter(char=char)]

    
    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs,
            table = self.Table(self.get_table_data())
        )
        # create or override -> don't cause 'get_context_data() got multiple values for keyword argument 'char''
        context["char"] = self.get_character()
        return context

    def post(self, request, *args, **kwargs):
        char = self.get_character()

        relabiliy_ids = set([int(st) for st in request.POST.keys() if st.isnumeric()])

        rels = []
        for rel in RelGfsAbility.objects.filter(id__in=relabiliy_ids, char=char):
            rel.notizen = request.POST.get(str(rel.id))
            rels.append(rel)

        RelGfsAbility.objects.bulk_update(rels, ["notizen"])

        # return response
        messages.success(request, "Erfolgreich gespeichert")
        return redirect(request.build_absolute_uri())
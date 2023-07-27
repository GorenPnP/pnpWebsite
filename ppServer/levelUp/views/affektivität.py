from django.db.models import Value
from django.contrib import messages
from django.shortcuts import redirect
from django.views.generic.base import TemplateView
from django.utils.decorators import method_decorator
from django.utils.html import format_html

import django_tables2 as tables

from base.abstract_views import GenericTable
from character.models import Affektivität

from ..decorators import is_erstellung_done
from ..forms import AffektivitätForm
from ..mixins import LevelUpMixin, LevelUpMixin


@method_decorator([is_erstellung_done], name="dispatch")
class AffektivitätView(LevelUpMixin, tables.SingleTableMixin, TemplateView):

    class Table(GenericTable):

        class Meta:
            attrs = GenericTable.Meta.attrs
            model = Affektivität
            fields = ["name", "wert", "notiz"]

        def render_wert(self, value, record):
            id = record.id
            return format_html(f"<input type='number' form='form' name='wert-{id}' value='{value}' min='-200' max='200' class='input'>")

        def render_notiz(self, value, record):
            id = record.id
            value = record.notizen
            return format_html(f"<textarea form='form' name='notizen-{id}'>{value}</textarea>")


    template_name = "levelUp/affektivität.html"
    model = Affektivität

    table_class = Table
    table_pagination = False

    def get_queryset(self):
        return Affektivität.objects.filter(char=self.get_character())\
            .annotate(notiz=Value(1))   # replace later
    
    def get_context_data(self, *args, **kwargs):
        return super().get_context_data(*args, **kwargs,
            table = self.Table(self.get_table_data()),
            form = AffektivitätForm(),
            topic = "Affektivität",
        )

    def post(self, request, *args, **kwargs):
        char = self.get_character()
        method = request.POST.get("method")

        if method == "update":

            # collect values
            wert_ids = {int(key.replace("wert-", "")): int(w) for key, w in request.POST.items() if "wert-" in key and len(w)}
            notizen_ids = {int(key.replace("notizen-", "")): n for key, n in request.POST.items() if "notizen-" in key}

            # test ids
            if len(wert_ids.keys()) != len(notizen_ids.keys()):
                messages.error(request, "Das Format habe ich nicht verstanden. Das waren unterschiedlich viele Werte und Notizen.")
                return redirect(request.build_absolute_uri())

            own_ids = [e.id for e in Affektivität.objects.filter(char=char)]
            for id, wert in wert_ids.items():
                if id not in own_ids or id not in notizen_ids.keys():
                    messages.error(request, "Das Format habe ich nicht verstanden. Die IDs waren durcheinander.")
                    return redirect(request.build_absolute_uri())

            # # apply them to db
            # TODO handle delete

            # update or create
            own_ids = [e.id for e in Affektivität.objects.filter(char=char)]
            for id, wert in wert_ids.items():
                Affektivität.objects.update_or_create(id=id, defaults={"wert": wert, "notizen": notizen_ids[id]})

        if method == "create":
            form = AffektivitätForm(request.POST)
            form.full_clean()
            form.cleaned_data["char"] = char

            # invalid?
            if not form.is_valid():
                messages.error(request, "Nicht valid")
                return redirect(request.build_absolute_uri())

            # add char
            aff = form.save(commit=False)
            aff.char = char
            aff.save()

        # return response
        messages.success(request, "Erfolgreich gespeichert")
        return redirect(request.build_absolute_uri())

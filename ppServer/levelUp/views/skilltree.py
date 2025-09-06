from django.db.models import Sum
from django.contrib import messages
from django.shortcuts import redirect
from django.views.generic.base import TemplateView
from django.utils.html import format_html
from django.utils.decorators import method_decorator

import django_tables2 as tables

from base.abstract_views import GenericTable
from character.models import GfsSkilltreeEntry, SkilltreeBase

from ..decorators import is_erstellung_done
from ..mixins import LevelUpMixin


@method_decorator([is_erstellung_done], name="dispatch")
class GenericSkilltreeView(LevelUpMixin, tables.SingleTableMixin, TemplateView):

    class Table(GenericTable):

        class Meta:
            attrs = GenericTable.Meta.attrs
            model = GfsSkilltreeEntry
            fields = ["chosen", "stufe", "text"]

        chosen = tables.Column(verbose_name="")

        def render_chosen(self, value, record):
            return format_html(f"<input type='checkbox' form='form' name='{record['stufe']}' {'checked disabled' if record['chosen'] else ''}>")

        def render_stufe(self, value, record):
            return format_html(f"<span class='stufe'>{value}</span> (<span class='sp'>{record['sp']}</span> SP)")



    template_name = "levelUp/skilltree.html"
    model = GfsSkilltreeEntry

    table_class = Table
    table_pagination = False

    def get_queryset(self):
        char = self.get_character()

        skilltree = [{"stufe": entry.stufe, "sp": entry.sp, "text": []} for entry in SkilltreeBase.objects.filter(stufe__gt=0).order_by("stufe")]
        entries = GfsSkilltreeEntry.objects.prefetch_related("base")\
            .filter(gfs=char.gfs, base__stufe__gt=0)\
            .order_by("base__stufe")

        # Gfs Skilltree
        for s in entries:

            # offset is -2, because anyone lacks the bonus (with Stufe 0) and starts at Stufe 2
            skilltree[s.base.stufe-2]["text"].append(s.__repr__())

        # list to string
        for s in skilltree: s["text"] = ", ".join(s["text"])

        
        return [{**s, "chosen": s["stufe"] <= char.skilltree_stufe} for s in skilltree]
    
    def get_context_data(self, *args, **kwargs):
        return super().get_context_data(*args, **kwargs,
            table = self.Table(self.get_table_data()),
            topic = "Skilltree"
        )

    def post(self, request, *args, **kwargs):
        char = self.get_character()

        skilltree_stufen = set([int(st) for st in request.POST.keys() if st.isnumeric()])
        max_stufe = max(skilltree_stufen) if skilltree_stufen else char.skilltree_stufe or 0
        skilltree = GfsSkilltreeEntry.objects.prefetch_related("base").filter(gfs=char.gfs, base__stufe__gt=char.skilltree_stufe, base__stufe__lte=max_stufe)

        # check

        # lower than before?
        print(char.skilltree_stufe, max_stufe)
        if char.skilltree_stufe > max_stufe:
            messages.error(request, "Die gewählte Stufe ist kleiner als die Jetzige.")
            return redirect(request.build_absolute_uri())
        
        # allowed, consecutive stufen?
        for st in skilltree_stufen:
            if not skilltree.filter(base__stufe=st).exists():
                messages.error(request, f"Stufe {st} hast du schon oder gibt es gar nicht")
                return redirect(request.build_absolute_uri())

        # affordable?
        sp_cost = SkilltreeBase.objects.filter(stufe__in=skilltree_stufen).aggregate(sp=Sum("sp"))["sp"] or 0
        if char.sp < sp_cost:
            messages.error(request, f"So viele SP hast du gar nicht")
            return redirect(request.build_absolute_uri())

        # pay
        char.sp -= sp_cost
        char.skilltree_stufe = max_stufe
        char.save(update_fields=["sp", "skilltree_stufe"])

        # collect values
        for s in skilltree: s.apply_to(char)

        # return response
        messages.success(request, "Erfolgreich gespeichert")
        return redirect(request.build_absolute_uri())
    
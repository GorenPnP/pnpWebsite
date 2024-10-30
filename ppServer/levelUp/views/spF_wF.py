from django.db.models import Subquery, OuterRef, Count, Sum, Value
from django.contrib import messages
from django.http.request import HttpRequest
from django.http.response import HttpResponse
from django.shortcuts import redirect
from django.views.generic.base import TemplateView
from django.utils.decorators import method_decorator
from django.utils.html import format_html

import django_tables2 as tables

from base.abstract_views import GenericTable
from character.models import Fertigkeit, Spezialfertigkeit, Wissensfertigkeit, RelSpezialfertigkeit, RelWissensfertigkeit
from ppServer.utils import ConcatSubquery

from ..decorators import is_erstellung_done
from ..mixins import LevelUpMixin


@method_decorator([is_erstellung_done], name="dispatch")
class GenericSpF_wFView(LevelUpMixin, tables.SingleTableMixin, TemplateView):

    class Table(GenericTable):

        class Meta:
            attrs = GenericTable.Meta.attrs

        titel = tables.Column(verbose_name="Fertigkeit")
        art = tables.Column(verbose_name="Art")
        attrs = tables.Column(verbose_name="Attribute")
        ferts = tables.Column(verbose_name="Fertigkeit/en")
        wp = tables.Column()

        def render_titel(self, value, record):
            return value
        
        def render_attrs(self, value, record):
            attrs = [record["attr1__titel"], record["attr2__titel"]]
            if "attr3__titel" in record:
                attrs.append(record["attr3__titel"])

            return ", ".join(sorted(attrs))

        def render_wp(self, value, record):
            value_exists = record["stufe"] is not None
            id = record["id"]

            args = ""
            if record["art"] == "Spezial":
                args += f"name='spezial-{id}' class='spezial-input'"
            else:
                args += f"name='wissen-{id}' class='wissen-input'"

            if value_exists:
                args += f" value='{record['stufe']}' required"

            return format_html(f"<input type='number' min='0' max='15' form='form' {args}>")



    template_name = "levelUp/spF_wF.html"

    table_class = Table
    table_pagination = False


    def get_context_data(self, *args, **kwargs):
        return super().get_context_data(*args, **kwargs,
            table = self.Table(self.get_table_data()),
            topic = "Spezial- & Wissensf."
        )


    def get_table_data(self):
        """
        Return the table data that should be used to populate the rows.
        """
        # if self.table_data is not None:
        #     return self.table_data
        char = self.get_character()

        spezial = list(
                Spezialfertigkeit.objects.all()\
                    .prefetch_related("attr1", "attr2")\
                    .annotate(
                        art = Value("Spezial"),
                        ferts = ConcatSubquery(Fertigkeit.objects.filter(spezialfertigkeit=OuterRef("pk")).order_by("titel").values("titel"), separator=", "),
                        attrs = Value(0),
                        stufe = Subquery(RelSpezialfertigkeit.objects.filter(char=char, spezialfertigkeit__id=OuterRef("id")).values("stufe")[:1]),
                        wp = Value(0), # replace later
                    )\
                    .values("id", "titel", "art",
                            "attrs", "attr1__titel", "attr2__titel",
                            "ferts", "wp", "stufe"
                    )
            )
        wissen = list(
                Wissensfertigkeit.objects.all()\
                    .prefetch_related("attr1", "attr2", "attr3")\
                    .annotate(
                        art = Value("Wissen"),
                        ferts = ConcatSubquery(Fertigkeit.objects.filter(wissensfertigkeit=OuterRef("pk")).order_by("titel").values("titel"), separator=", "),
                        attrs = Value(0),
                        stufe = Subquery(RelWissensfertigkeit.objects.filter(char=char, wissensfertigkeit__id=OuterRef("id")).values("stufe")[:1]),
                        wp = Value(0),
                    )\
                    .values("id", "titel", "art",
                            "attrs", "attr1__titel", "attr2__titel", "attr3__titel",
                            "ferts", "stufe", "wp"
                    )
            )

        # return objects (ordered by name)
        return sorted(spezial + wissen, key=lambda x: x["titel"])


    def get(self, request, *args, **kwargs):
        messages.info(request, "Zum Erlernen '0' eintragen, höher geht nur mit mit WP bei Erstellung")
        return super().get(request, *args, **kwargs)

    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        char = self.get_character()

        # collect values
        payment_method = request.POST.get("payment_method")
        spezial_ids = {int(key.replace("spezial-", "")): int(stufe) for key, stufe in request.POST.items() if "spezial-" in key and len(stufe)}
        wissen_ids = {int(key.replace("wissen-", "")): int(stufe) for key, stufe in request.POST.items() if "wissen-" in key and len(stufe)}

        # test them
        if payment_method not in ["points", "sp"]:
            messages.error(request, "Die Zahlungsart für neue Fertigkeiten kenne ich nicht.")

        spezial = RelSpezialfertigkeit.objects\
            .filter(char=char)\
            .aggregate(
                wp = Sum("stufe"),
                fert = Count("*")
            )
        wissen_qs = RelWissensfertigkeit.objects.filter(char=char)
        wissen_wp = sum(wissen_qs.values_list("stufe", flat=True))

        fert_max = (spezial["fert"] or 0) + (wissen_qs.count() or 0) + char.spF_wF
        wp_max = (spezial["wp"] or 0) + (wissen_wp or 0) + char.wp
        fert_max = char.spF_wF if payment_method == "points" else char.sp
        fert_max += (spezial["fert"] or 0) + (wissen_qs.count() or 0)

        # enough to pay for new ferts?
        if len(spezial_ids) + len(wissen_ids) > fert_max:
            messages.error(request, "Du hast zu viele gewählt")

        # enough wp?
        if sum(spezial_ids.values()) + sum(wissen_ids.values()) > wp_max:
            messages.error(request, "Du hast zu viele WP verteilt")

        # permit selling stufe
        faulty_spezial = [rel.spezialfertigkeit.titel for rel in RelSpezialfertigkeit.objects.prefetch_related("spezialfertigkeit").filter(char=char) if rel.spezialfertigkeit.id not in spezial_ids.keys() or spezial_ids[rel.spezialfertigkeit.id] < rel.stufe]
        faulty_wissen = [rel.wissensfertigkeit.titel for rel in RelWissensfertigkeit.objects.prefetch_related("wissensfertigkeit").filter(char=char) if rel.wissensfertigkeit.id not in wissen_ids.keys() or wissen_ids[rel.wissensfertigkeit.id] < rel.stufe]
        if len(faulty_spezial) + len(faulty_wissen) > 0:
            messages.error(request, f"Du kannst keine Stufen (von {', '.join([*faulty_spezial, *faulty_wissen])}) verkaufen")


        # all fine or not?
        if len(messages.get_messages(request)):
            return redirect(request.build_absolute_uri())

        # apply them to db
        if payment_method == "points":
            char.spF_wF = fert_max - len(spezial_ids) - len(wissen_ids)
        else:
            char.sp = fert_max - len(spezial_ids) - len(wissen_ids)
        char.wp = wp_max - sum(spezial_ids.values()) - sum(wissen_ids.values())
        char.save(update_fields=["spF_wF", "sp", "wp"])

        RelSpezialfertigkeit.objects.filter(char=char).delete()
        RelWissensfertigkeit.objects.filter(char=char).delete()
        for sp in Spezialfertigkeit.objects.filter(id__in=spezial_ids):
            RelSpezialfertigkeit.objects.create(char=char, spezialfertigkeit=sp, stufe=spezial_ids[sp.id])
        for wi in Wissensfertigkeit.objects.filter(id__in=wissen_ids):
            RelWissensfertigkeit.objects.create(char=char, wissensfertigkeit=wi, stufe=wissen_ids[wi.id])

        # return response
        messages.success(request, "Erfolgreich gespeichert")
        return redirect(request.build_absolute_uri())

from django.shortcuts import get_object_or_404, redirect
from django.views.decorators.http import require_POST
from django.urls import reverse

from cards.models import Transaction
from character.models.char import Charakter
from log.create_log import logAuswertung
from core.decorators import spielleitung_only, verified_account

from .forms import AuswertungForm, LarpAuswertungForm

@require_POST
@verified_account
@spielleitung_only()
def post_auswertung(request, *args, **kwargs):
    object = get_object_or_404(Charakter.objects.prefetch_related("card"), pk=kwargs["pk"])
    if (object.eigentümer == None or object.in_erstellung == True):
                return redirect("character:show", args=[object.pk])

    form = LarpAuswertungForm(request.POST) if object.larp else AuswertungForm(request.POST)
    form.full_clean()
    if form.is_valid():
        fields = {**form.cleaned_data}
        story = fields.pop("story", "") or "Zwischenauswertung"

        # apply geld
        geld = fields.pop("geld")
        if geld:
            object.card.money += geld
            object.card.save(update_fields=["money"])
            Transaction.objects.create(receiver=object.card, amount=geld, reason=f"Storybelohnung '{story}'")

        # apply all other/numeric fields
        for k, v in fields.items():
            old_value = getattr(object, k)
            setattr(object, k, old_value + v)

        object.save(update_fields=fields)

        logAuswertung(object.eigentümer, object, story, {**fields, "geld": geld})

        # check ep for new stufe
        object.init_stufenhub()

        return redirect(reverse("character:show", args=[object.pk]))

    return redirect(request.build_absolute_uri())

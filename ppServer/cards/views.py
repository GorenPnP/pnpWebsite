from typing import Any, Dict
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import UserPassesTestMixin
from django.http import HttpResponseNotFound
from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.views.generic import DetailView
from django.views.generic.list import ListView

from ppServer.decorators import spielleiter_only

from .forms import *

class CardListView(ListView):

    model = Card
    template_name = "cards/index.html"
    # paginate_by = 100  # if pagination is desired

    def get_queryset(self):
        spieler = self.request.spieler.instance
        if not spieler: return HttpResponseNotFound()

        return self.model.objects.filter(spieler=spieler, active=True)
    
    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        return super().get_context_data(**kwargs, topic="Meine Karten")


class CardDetailView(UserPassesTestMixin, DetailView):

    model = Card
    template_name = "cards/show.html"

    def test_func(self):
        spieler = self.request.spieler.instance
        if not spieler: return HttpResponseNotFound()

        return self.get_object().spieler == spieler and self.get_object().active

    def handle_no_permission(self):
        return HttpResponseNotFound()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        spieler = self.request.spieler.instance
        if not spieler: return HttpResponseNotFound()

        if context["object"].spieler.id != spieler.id:
            return {}

        context["transactions"] = context["object"].get_transactions()
        context["topic"] = context["object"].name
        context["app_index"] = "Konten"
        context["app_index_url"] = reverse("cards:index")

        return context


@spielleiter_only(redirect_to="cards:index")
def sp_transaction(request):
    errors = []

    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = AdminTransactionForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            
            if form.cleaned_data["sender"].money < form.cleaned_data["amount"]:
                errors.append("Der Sender hat nur {} Dr., nicht {} Dr.".format(
                    form.cleaned_data["sender"].money,
                    form.cleaned_data["amount"]
                ))

            else:
                # process the data in form.cleaned_data as required

                form.cleaned_data["sender"].money -= form.cleaned_data["amount"]
                form.cleaned_data["sender"].save(update_fields=["money"])

                form.cleaned_data["receiver"].money += form.cleaned_data["amount"]
                form.cleaned_data["receiver"].save(update_fields=["money"])

                form.save()

                # redirect to a new URL:
                return redirect('admin:cards_transaction_changelist')

    # if a GET (or any other method) we'll create a blank form
    else:
        form = AdminTransactionForm()

    return render(request, 'cards/transaction.html', {'form': form, "errors": errors, "topic": "Neue Transaktion"})


@login_required
def transaction_card_id(request, card_id):
    card = get_object_or_404(Card, card_id=card_id, active=True)
    return redirect(reverse("cards:transaction", args=[card.id]))


@login_required
def transaction(request, uuid):
    errors = []
    spieler = request.spieler.instance
    if not spieler: return HttpResponseNotFound()

    sender = get_object_or_404(Card, id=uuid)

    if not sender.active or (
        not request.spieler.is_spielleiter and not sender.spieler == spieler
    ):
        return HttpResponseNotFound()

    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = SpielerTransactionForm(request.POST, uuid=uuid)
        # check whether it's valid:
        if form.is_valid():
            
            if sender.money < form.cleaned_data["amount"]:
                errors.append("Der Sender hat nur {} Dr., nicht {} Dr.".format(
                    sender.money,
                    form.cleaned_data["amount"]
                ))

            else:
                # process the data in form.cleaned_data as required

                sender.money -= form.cleaned_data["amount"]
                sender.save(update_fields=["money"])

                form.cleaned_data["receiver"].money += form.cleaned_data["amount"]
                form.cleaned_data["receiver"].save(update_fields=["money"])
                transaction = form.save()

                transaction.sender = sender
                transaction.save(update_fields=["sender"])

                # redirect to a new URL:
                return redirect(reverse('cards:show', args=[uuid]))

    # if a GET (or any other method) we'll create a blank form
    else:
        form = SpielerTransactionForm(uuid=uuid)

    return render(request, 'cards/transaction.html', {
        'form': form,
        "errors": errors,
        "sender": sender,
        "topic": "Neue Transaktion",
        "app_index": "Konten",
        "app_index_url": reverse("cards:index"),
    })
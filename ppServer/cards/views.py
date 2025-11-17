from typing import Any, Dict
from django.contrib.auth.mixins import UserPassesTestMixin
from django.http import HttpResponseNotFound
from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.views.generic import DetailView
from django.views.generic.base import TemplateView
from django.views.generic.list import ListView

from ppServer.decorators import spielleitung_only, verified_account
from ppServer.mixins import VerifiedAccountMixin

from .forms import *

class CardListView(VerifiedAccountMixin, ListView):

    model = Card
    template_name = "cards/index.html"
    # paginate_by = 100  # if pagination is desired

    def get_queryset(self):
        return self.model.objects.filter(spieler=self.request.spieler.instance, active=True)
    
    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        return super().get_context_data(**kwargs, topic="Meine Konten")


class CardDetailView(VerifiedAccountMixin, UserPassesTestMixin, TemplateView):
    template_name = "cards/show.html"

    object = None
    def get_object(self):
        if not self.object:
            self.object = Card.objects.prefetch_related("spieler", "char__eigentümer").get(pk=self.kwargs["pk"])
        return self.object
        

    def test_func(self):
        object = self.get_object()
        return (
            (self.request.spieler.is_spielleitung or object.account_owner == self.request.spieler.instance) and
            object.active
        )

    def handle_no_permission(self):
        return HttpResponseNotFound()

    def get_context_data(self, **kwargs):
        object = self.get_object()
        return {
            **super().get_context_data(**kwargs),
            "object": self.get_object(),
            "transactions": object.get_transactions(),
            "topic": object.account_name,
            "app_index": "Konten",
            "app_index_url": reverse("cards:index"),
        }


@verified_account
@spielleitung_only(redirect_to="cards:index")
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


@verified_account
def redirect_transactions(request, card_id: int):
    card = get_object_or_404(Card.objects.prefetch_related("spieler", "char__eigentümer"), card_id=card_id)
    return redirect(reverse("cards:transaction", args=[card.id]))


class TransactionView(VerifiedAccountMixin, UserPassesTestMixin, TemplateView):
    template_name = 'cards/transaction.html'

    def get_sender(self):
        return get_object_or_404(Card.objects.prefetch_related("spieler", "char__eigentümer"), id=self.kwargs["uuid"])

    def test_func(self):
        sender = self.get_sender()

        return sender.active and (
            self.request.spieler.is_spielleitung or
            sender.account_owner == self.request.spieler.instance
        )

    def handle_no_permission(self):
        return HttpResponseNotFound()
    

    def get_context_data(self, *args, **kwargs):
        return super().get_context_data(
            *args, **kwargs,
            errors = [],
            sender = self.get_sender(),
            topic = "Neue Transaktion",
            app_index = "Konten",
            app_index_url = reverse("cards:index"),
        )

    def get(self, *args, **kwargs):
        return super().get(*args, **kwargs, form=SpielerTransactionForm(uuid=self.kwargs["uuid"]))

    def post(self, *args, **kwargs):
        errors = []

        # create a form instance and populate it with data from the request:
        form = SpielerTransactionForm(self.request.POST, uuid=self.kwargs["uuid"])
        # check whether it's valid:
        if form.is_valid():
            sender = self.get_sender()

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
                return redirect(reverse('cards:show', args=[self.kwargs["uuid"]]))

        if errors:
            return render(self.request, self.template_name, {
                **self.get_context_data(),
                'form': form,
                "errors": errors,
            })
        return redirect(self.request.build_absolute_uri())

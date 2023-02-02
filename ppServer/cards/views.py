from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import UserPassesTestMixin
from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.views.generic import DetailView
from django.views.generic.list import ListView

from ppServer.decorators import spielleiter_only
from character.models import Spieler

from .forms import *

class CardListView(ListView):

    model = Card
    template_name = "cards/index.html"
    # paginate_by = 100  # if pagination is desired

    def get_queryset(self):
        spieler = get_object_or_404(Spieler, name=self.request.user.username)
        return self.model.objects.filter(spieler=spieler, active=True)


class CardDetailView(UserPassesTestMixin, DetailView):

    model = Card
    template_name = "cards/show.html"

    def test_func(self):
        spieler = get_object_or_404(Spieler, name=self.request.user.username)
        return self.get_object().spieler == spieler and self.get_object().active

    def handle_no_permission(self):
        return redirect("test404")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        spieler = get_object_or_404(Spieler, name=self.request.user.username)
        if context["object"].spieler.id != spieler.id:
                return {}

        context["transactions"] = context["object"].get_transactions()

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
                form.cleaned_data["sender"].save()

                form.cleaned_data["receiver"].money += form.cleaned_data["amount"]
                form.cleaned_data["receiver"].save()

                form.save()

                # redirect to a new URL:
                return redirect('admin:cards_transaction_changelist')

    # if a GET (or any other method) we'll create a blank form
    else:
        form = AdminTransactionForm()

    return render(request, 'cards/transaction.html', {'form': form, "errors": errors})


@login_required
def transaction(request, uuid):
    errors = []
    spieler = get_object_or_404(Spieler, name=request.user.username)
    sender = get_object_or_404(Card, id=uuid)

    if not sender.active or (
        not request.user.groups.filter(name__iexact="spielleiter").exists() and not sender.spieler == spieler
    ):
        return redirect(reverse("test404"))

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
                sender.save()

                form.cleaned_data["receiver"].money += form.cleaned_data["amount"]
                form.cleaned_data["receiver"].save()
                transaction = form.save()

                transaction.sender = sender
                transaction.save()

                # redirect to a new URL:
                return redirect(reverse('cards:show', args=[uuid]))

    # if a GET (or any other method) we'll create a blank form
    else:
        form = SpielerTransactionForm(uuid=uuid)

    return render(request, 'cards/transaction.html', {'form': form, "errors": errors, "sender": sender})
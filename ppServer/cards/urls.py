from django.contrib.auth.decorators import login_required
from django.urls import path

from .views import *

app_name = 'cards'

urlpatterns = [
    path('', login_required(CardListView.as_view()), name='index'),
    path('transaction/', sp_transaction, name='sp_transaction'),
    path('transaction/card/<int:card_id>/', transaction_card_id, name='transaction_card_id'),
    path('transaction/<slug:uuid>/', transaction, name='transaction'),
    path('<slug:pk>/', login_required(CardDetailView.as_view()), name='show'),          # has to be the last one since slug matches everything
]

from django.urls import path

from .views import *

app_name = 'cards'

urlpatterns = [
    path('', CardListView.as_view(), name='index'),
    path('transaction/', sp_transaction, name='sp_transaction'),
    path('transaction/card/<int:card_id>', redirect_transactions, name='redirect_transactions'),    # saved on NFC chip of cards
    path('transaction/<slug:uuid>/', TransactionView.as_view(), name='transaction'),
    path('<uuid:pk>/', CardDetailView.as_view(), name='show'),          # has to be the last one since slug matches everything
]

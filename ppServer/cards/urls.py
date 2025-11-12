from django.urls import path

from .views import *

app_name = 'cards'

urlpatterns = [
    path('', CardListView.as_view(), name='index'),
    path('transaction/', sp_transaction, name='sp_transaction'),
    path('transaction/<slug:uuid>/', TransactionView.as_view(), name='transaction'),
    path('<uuid:pk>/', CardDetailView.as_view(), name='show'),          # has to be the last one since slug matches everything
]

from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from django.urls import path
from . import views

app_name = 'polls'

urlpatterns = [
    path('<int:pk>/', views.DetailView, name='detail'),
    # path('<int:pk>/', views.detail, name='detail'),
    path('<int:pk>/results/', views.results, name='results'),
]

from django.urls import path

from . import views

app_name = 'character'

urlpatterns = [
    path('', views.index, name='index'),
    path('<int:pk>/', views.show, name='show'),
]

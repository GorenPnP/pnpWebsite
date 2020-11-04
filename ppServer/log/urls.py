from django.urls import path
from . import views

app_name = 'log'

urlpatterns = [
    path('', views.userLog, name='index'),
]

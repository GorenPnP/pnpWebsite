from django.urls import path

from . import views

app_name = 'time_space'

urlpatterns = [
    path('', views.index, name='index'),
    path('net/<int:id>', views.net, name='net'),
    path('createNet', views.createNet, name='createNet')
]

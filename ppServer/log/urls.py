from django.urls import path
from . import views

app_name = 'log'

urlpatterns = [
    path('', views.UserLogView.as_view(), name='index'),
    path('admin', views.AdminLogView.as_view(), name='admin'),
]

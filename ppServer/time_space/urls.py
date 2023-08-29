from django.urls import path

from . import views

app_name = 'time_space'

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('net/<int:pk>', views.PlayNetView.as_view(), name='net'),
    path('editNet/<int:pk>', views.EditNetView.as_view(), name='editNet'),
    path('createNet', views.EditNetView.as_view(), name='createNet'),
    path('manual', views.ManualView.as_view(), name='manual'),
]

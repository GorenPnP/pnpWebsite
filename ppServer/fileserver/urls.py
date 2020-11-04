from django.urls import path
from . import views

app_name = 'file'

urlpatterns = [

    path('', views.maps, name='index'),
    path('<int:mapID>/', views.show_map, name='map'),
]

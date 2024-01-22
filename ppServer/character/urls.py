from django.urls import path

from . import views

app_name = 'character'

urlpatterns = [
    path('', views.CharacterListView.as_view(), name='index'),
    path('<int:pk>/', views.ShowView.as_view(), name='show'),
    path('history/<int:pk>/', views.HistoryView.as_view(), name='history'),

    path('use_item/<str:relshop_model>/<int:pk>/', views.use_relshop, name='use_item'),
]

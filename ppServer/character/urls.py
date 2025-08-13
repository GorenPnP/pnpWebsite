from django.urls import path

from . import views

app_name = 'character'

urlpatterns = [
    path('', views.CharacterListView.as_view(), name='index'),
    path('<int:pk>/', views.ShowView.as_view(), name='show'),
    path('history/<int:pk>/', views.HistoryView.as_view(), name='history'),
    path('delete/<int:pk>/', views.delete_char, name='delete'),
    path('create/', views.CreateCharacterView.as_view(), name='create'),

    path('edit_tag/<int:pk>/', views.edit_tag, name='edit_tag'),
    path('delete_tag/<int:pk>/', views.delete_tag, name='delete_tag'),
    path('use_item/<str:relshop_model>/<int:pk>/', views.use_relshop, name='use_item'),
]

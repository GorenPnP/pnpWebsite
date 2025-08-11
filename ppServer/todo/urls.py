from django.urls import path

from . import views

app_name = 'todo'

urlpatterns = [
    path('', views.CalendarOverview.as_view(), name='calendar'),
    path('add/', views.add_category, name='add_category'),
    path('delete/<int:pk>/', views.delete_category, name='delete_category'),
    path('add_interval/<int:pk>/', views.add_interval, name='add_interval'),
    path('delete_interval/<int:pk>/<str:day>/', views.delete_interval, name='delete_interval'),
]

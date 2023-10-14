from django.urls import path

from . import views

app_name = 'campaign'

urlpatterns = [
	path('auswertung/', views.AuswertungListView.as_view(), name='auswertung_hub'),
	path('auswertung/<int:pk>/', views.AuswertungView.as_view(), name='auswertung'),
]

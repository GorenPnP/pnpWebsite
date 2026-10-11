from django.urls import path

from .views import *

app_name = 'campaign'

urlpatterns = [
	path('auswertung/<int:pk>/', post_auswertung, name='auswertung'),
]

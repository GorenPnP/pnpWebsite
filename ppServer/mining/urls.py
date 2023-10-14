from django.urls import path
from django.views.generic import TemplateView

from . import views

app_name = 'mining'

urlpatterns = [
	path('', views.region_select, name='region_select'),
	path('create_region/', views.region_editor, name='create_region'),
	path('region_editor/<int:region_id>/', views.region_editor, name='region_editor'),

	path('shooter/', TemplateView.as_view(template_name="mining/shooter.html"), name='shooter'),
	path('game/<int:pk>/', views.game, name='game')
]

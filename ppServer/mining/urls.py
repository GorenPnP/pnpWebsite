from django.urls import path

from . import views

app_name = 'mining'

urlpatterns = [
	path('', views.region_select, name='region_select'),
	path('create_region', views.region_editor, name='create_region'),
	path('region_editor/<int:region_id>', views.region_editor, name='region_editor'),
	path('<int:pk>', views.mining, name='mining'),

	path('shooter', views.shooter, name='shooter'),
	path('game/<int:pk>', views.game, name='game')
]

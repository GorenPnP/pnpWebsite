from django.urls import path

from . import views
from .api_views import get_mc_recipes

app_name = 'crafting'

urlpatterns = [
	path('', views.index, name='index'),
	path('inventory/', views.inventory, name='inventory'),
	path('craft/', views.craft, name='craft'),
	path('details/<int:id>/', views.details, name='details'),
	path('sp_give_items/', views.sp_give_items, name='sp_give_items'),

	path('api/mc_recipes/', get_mc_recipes, name='api_mc_recipes'),
]

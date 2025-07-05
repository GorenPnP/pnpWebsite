from django.urls import path

from . import views
from .api_views import GetMinecraftRecipesView

app_name = 'crafting'

urlpatterns = [
	path('', views.IndexView.as_view(), name='index'),
	path('inventory/', views.InventoryView.as_view(), name='inventory'),
	path('craft/', views.CraftingView.as_view(), name='craft'),
	path('details/<int:pk>/', views.RecipeDetailsView.as_view(), name='details'),
	path('sp_give_items/', views.SpGiveItemsView.as_view(), name='sp_give_items'),
	path('regions/', views.RegionListView.as_view(), name='regions'),
	path('mining/<int:pk>/', views.MiningView.as_view(), name='mining'),

	path('api/mc_recipes/', GetMinecraftRecipesView.as_view(), name='api_mc_recipes'),
]

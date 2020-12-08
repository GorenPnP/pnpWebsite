from django.urls import path

from . import views

app_name = 'crafting'

urlpatterns = [
	path('', views.index, name='index'),
	path('inventory', views.inventory, name='inventory'),
	path('craft', views.craft, name='craft'),
	path('details/<int:id>', views.details, name='details'),
	path('sp_give_items', views.sp_give_items, name='sp_give_items'),
]

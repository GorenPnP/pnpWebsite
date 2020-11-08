from django.urls import path

from .views import *

app_name = 'crafting'

urlpatterns = [
	path('', index, name='index'),
	path('inventory', inventory, name='inventory'),
	path('craft', craft, name='craft'),
	path('details/<int:id>', details, name='details'),
	path('sp_give_items', sp_give_items, name='sp_give_items'),
]

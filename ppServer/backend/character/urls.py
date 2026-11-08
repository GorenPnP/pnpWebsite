from django.apps import apps
from django.urls import path, register_converter
from django.views.decorators.http import require_GET, require_POST

from shop.converter import get_ModelNameConverter
from shop.views.list import shopmodel_upgrade_list

from . import views
from .models.relshop import RelShop

app_name = 'character'

register_converter(get_ModelNameConverter("shop", shopmodel_upgrade_list), "shopmodel")
register_converter(get_ModelNameConverter("character", [m for m in apps.get_models("character") if issubclass(m, RelShop)]), "relshopmodel")
urlpatterns = [
    path('', views.CharacterListView.as_view(), name='index'),
    path('<int:pk>/', views.ShowView.as_view(), name='show'),
    path('history/<int:pk>/', views.HistoryView.as_view(), name='history'),
    path('delete/<int:pk>/', views.delete_char, name='delete'),
    path('create/', views.CreateCharacterView.as_view(), name='create'),
    path('upgrades/<int:pk>/', require_GET(views.EditUpgrades.as_view()), name='upgrades'),
    path('upgrades/<int:pk>/<shopmodel:shop_model>/<int:item_pk>', require_POST(views.EditUpgrades.as_view()), name='upgrades_post'),
    path('item_upgrades/<relshopmodel:shop_model>/<int:pk>', views.RelItemUpgradeDetailView.as_view(), name='relitem_upgrade_detail'),

    path('edit_tag/<int:pk>/', views.edit_tag, name='edit_tag'),
    path('delete_tag/<int:pk>/', views.delete_tag, name='delete_tag'),
    path('add_ramsch/<int:pk>/', views.add_ramsch, name='add_ramsch'),
    path('spend_money/<int:pk>/', views.spend_money, name='spend_money'),
    path('remove_sp/<int:pk>/', views.remove_sp, name='remove_sp'),
    path('remove_item/<relshopmodel:rel_model>/<int:pk>/', views.remove_relshop, name='remove_item'),
    path('save_item_notizen/<str:relshop_model>/<int:pk>/', views.save_item_notizen, name='save_item_notizen'),
    path('save_story_notes/<int:pk>/', views.save_story_notes, name='save_story_notes'),
]

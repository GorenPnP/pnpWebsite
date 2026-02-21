from django.urls import path, register_converter

from .converter import *
from .views.index import index, review_items, transfer_items, propose_item, shopmodel_list
from .views.buy import BuyView
from .views import list as listViews

app_name = 'shop'
register_converter(get_ModelNameConverter(app_name, shopmodel_list), "model")
register_converter(get_ModelNameConverter(app_name, [m for m in shopmodel_list if m._meta.model_name != "tinker"]), "buyable_model")

urlpatterns = [
    path('', index, name='index'),
    path('review/', review_items, name='review_items'),
    path('transfer-items/', transfer_items, name='transfer_items'),
    path('propose/<model:model>/', propose_item, name="propose"),

    path('all/', listViews.FullShopTableView.as_view(), name='all'),

    path('items/', listViews.ItemTableView.as_view(), name='item_list'),
    path('waffen_werkzeuge/', listViews.WaffenWerkzeugeTableView.as_view(), name='waffen_werkzeuge_list'),
    path('magazine/', listViews.MagazinTableView.as_view(), name='magazin_list'),
    path('pfeile_bolzen/', listViews.PfeilBolzenTableView.as_view(), name='pfeil_bolzen_list'),
    path("schusswaffen", listViews.SchusswaffenTableView.as_view(), name='schusswaffen_list'),
    path('magische_ausrüstung/', listViews.MagischeAusrüstungTableView.as_view(), name='magische_ausrüstung_list'),
    path('rituale_runen/', listViews.RitualeRunenTableView.as_view(), name='rituale_runen_list'),
    path('rüstungen/', listViews.RüstungTableView.as_view(), name='rüstung_list'),
    path('ausruestung_technik/', listViews.AusrüstungTechnikTableView.as_view(), name='ausrüstung_technik_list'),
    path('fahrzeuge/', listViews.FahrzeugTableView.as_view(), name='fahrzeug_list'),
    path('einbauten/', listViews.EinbautenTableView.as_view(), name='einbauten_list'),
    path('zauber/', listViews.ZauberTableView.as_view(), name='zauber_list'),
    path('alchemie/', listViews.AlchemieTableView.as_view(), name='alchemie_list'),
    path('tinker/', listViews.TinkerTableView.as_view(), name='tinker_list'),
    path('begleiter/', listViews.BegleiterTableView.as_view(), name='begleiter_list'),
    path('engelsroboter/', listViews.EngelsroboterTableView.as_view(), name='engelsroboter_list'),

    path('buy_<buyable_model:model>/<int:id>/', BuyView.as_view(), name="buy"),
]

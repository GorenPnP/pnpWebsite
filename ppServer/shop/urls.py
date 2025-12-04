from django.urls import path

from .views.index import index, review_items, transfer_items, propose_item
from .views import buy as buyViews
from .views import list as listViews

app_name = 'shop'

urlpatterns = [
    path('', index, name='index'),
    path('review/', review_items, name='review_items'),
    path('transfer-items/', transfer_items, name='transfer_items'),
    path('propose/<slug:model>/', propose_item, name="propose"),

    path('all/', listViews.FullShopTableView.as_view(), name='all'),

    path('items/', listViews.ItemTableView.as_view(), name='item_list'),
    path('waffen_werkzeuge/', listViews.WaffenWerkzeugeTableView.as_view(), name='waffen_werkzeuge_list'),
    path('magazine/', listViews.MagazinTableView.as_view(), name='magazin_list'),
    path('pfeile_bolzen/', listViews.PfeilBolzenTableView.as_view(), name='pfeil_bolzen_list'),
    path("schusswaffen", listViews.SchusswaffenTableView.as_view(), name='schusswaffen_list'),
    path('magische_ausrüstung/', listViews.MagischeAusrüstungTableView.as_view(), name='magische_ausrüstung_list'),
    path('rituale_runen/', listViews.RitualeRunenTableView.as_view(), name='rituale_runen_list'),
    path('ruestungen/', listViews.RüstungenTableView.as_view(), name='rüstungen_list'),
    path('ausruestung_technik/', listViews.AusrüstungTechnikTableView.as_view(), name='ausrüstung_technik_list'),
    path('fahrzeuge/', listViews.FahrzeugTableView.as_view(), name='fahrzeug_list'),
    path('einbauten/', listViews.EinbautenTableView.as_view(), name='einbauten_list'),
    path('zauber/', listViews.ZauberTableView.as_view(), name='zauber_list'),
    path('vergessene_zauber/', listViews.VergessenerZauberTableView.as_view(), name='vergessenerzauber_list'),
    path('alchemie/', listViews.AlchemieTableView.as_view(), name='alchemie_list'),
    path('tinker/', listViews.TinkerTableView.as_view(), name='tinker_list'),
    path('begleiter/', listViews.BegleiterTableView.as_view(), name='begleiter_list'),
    path('engelsroboter/', listViews.EngelsroboterTableView.as_view(), name='engelsroboter_list'),

    path('buy_item/<int:id>/', buyViews.ItemBuyView.as_view(), name="buy_item"),
    path('buy_waffen_werkzeuge/<int:id>/', buyViews.Waffen_WerkzeugeBuyView.as_view(), name="buy_waffen_werkzeuge"),
    path('buy_magazin/<int:id>/', buyViews.MagazinBuyView.as_view(), name="buy_magazin"),
    path('buy_pfeile_bolzen/<int:id>/', buyViews.Pfeil_BolzenBuyView.as_view(), name="buy_pfeil_bolzen"),
    path('buy_schusswaffen/<int:id>/', buyViews.SchusswaffenBuyView.as_view(), name="buy_schusswaffen"),
    path('buy_magische_ausrüstung/<int:id>/', buyViews.Magische_AusrüstungBuyView.as_view(), name="buy_magische_ausrüstung"),
    path('buy_rituale_runen/<int:id>/', buyViews.Rituale_RunenBuyView.as_view(), name='buy_rituale_runen'),
    path('buy_ruestungen/<int:id>/', buyViews.RüstungBuyView.as_view(), name="buy_rüstungen"),
    path('buy_ausruestung_technik/<int:id>/', buyViews.Ausrüstung_TechnikBuyView.as_view(), name="buy_ausrüstung_technik"),
    path('buy_fahrzeuge/<int:id>/', buyViews.FahrzeugBuyView.as_view(), name="buy_fahrzeug"),
    path('buy_einbauten/<int:id>/', buyViews.EinbautenBuyView.as_view(), name="buy_einbauten"),
    path('buy_zauber/<int:id>/', buyViews.ZauberBuyView.as_view(), name="buy_zauber"),
    path('buy_vergessener_zauber/<int:id>/', buyViews.VergessenerZauberBuyView.as_view(), name="buy_vergessenerzauber"),
    path('buy_alchemie/<int:id>/', buyViews.AlchemieBuyView.as_view(), name="buy_alchemie"),
    path('buy_begleiter/<int:id>/', buyViews.BegleiterBuyView.as_view(), name="buy_begleiter"),
    path('buy_engelsroboter/<int:id>/', buyViews.EngelsroboterBuyView.as_view(), name="buy_engelsroboter"),
]

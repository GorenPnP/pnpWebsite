from django.urls import path

from .views.index import index, review_items
from .views import buy as buyViews
from .views import list as listViews

app_name = 'shop'

urlpatterns = [
    path('', index, name='index'),
    path('review', review_items, name='review_items'),

    path('all', listViews.FullShopTableView.as_view(), name='all'),

    path('items', listViews.ItemTableView.as_view(), name='items'),
    path('waffen_werkzeuge', listViews.WaffenWerkzeugeTableView.as_view(), name='waffen_werkzeuge'),
    path('magazine', listViews.MagazinTableView.as_view(), name='magazine'),
    path('pfeile_bolzen', listViews.PfeilBolzenTableView.as_view(), name='pfeile_bolzen'),
    path("schusswaffen", listViews.SchusswaffenTableView.as_view(), name='schusswaffen'),
    path('magische_ausrüstung', listViews.MagischeAusrüstungTableView.as_view(), name='magische_ausrüstung'),
    path('rituale_runen', listViews.RitualeRunenTableView.as_view(), name='rituale_runen'),
    path('ruestungen', listViews.RüstungenTableView.as_view(), name='rüstungen'),
    path('ausruestung_technik', listViews.AusrüstungTechnikTableView.as_view(), name='ausr_technik'),
    path('fahrzeuge', listViews.FahrzeugTableView.as_view(), name='fahrzeuge'),
    path('einbauten', listViews.EinbautenTableView.as_view(), name='einbauten'),
    path('zauber', listViews.ZauberTableView.as_view(), name='zauber'),
    path('vergessene_zauber', listViews.VergessenerZauberTableView.as_view(), name='vergessene_zauber'),
    path('alchemie', listViews.AlchemieTableView.as_view(), name='alchemie'),
    path('tinker', listViews.TinkerTableView.as_view(), name='tinker'),
    path('begleiter', listViews.BegleiterTableView.as_view(), name='begleiter'),

    path('buy_item/<int:id>', buyViews.buy_item, name="buy_item"),
    path('buy_waffen_werkzeuge/<int:id>', buyViews.buy_waffen_werkzeuge, name="buy_waffen_werkzeuge"),
    path('buy_magazin/<int:id>', buyViews.buy_magazin, name="buy_magazin"),
    path('buy_pfeile_bolzen/<int:id>', buyViews.buy_pfeil_bolzen, name="buy_pfeil_bolzen"),
    path('buy_schusswaffen/<int:id>', buyViews.buy_schusswaffe, name="buy_schusswaffen"),
    path('buy_magische_ausrüstung/<int:id>', buyViews.buy_magische_ausrüstung, name="buy_magische_ausrüstung"),
    path('buy_rituale_runen/<int:id>', buyViews.buy_rituale_runen, name='buy_rituale_runen'),
    path('buy_ruestungen/<int:id>', buyViews.buy_rüstung, name="buy_rüstungen"),
    path('buy_ausruestung_technik/<int:id>', buyViews.buy_ausrüstung_technik, name="buy_ausrüstung_technik"),
    path('buy_fahrzeuge/<int:id>', buyViews.buy_fahrzeug, name="buy_fahrzeug"),
    path('buy_einbauten/<int:id>', buyViews.buy_einbauten, name="buy_einbauten"),
    path('buy_zauber/<int:id>', buyViews.buy_zauber, name="buy_zauber"),
    path('buy_vergessener_zauber/<int:id>', buyViews.buy_vergessener_zauber, name="buy_vergessenerzauber"),
    path('buy_alchemie/<int:id>', buyViews.buy_alchemie, name="buy_alchemie"),
    path('buy_begleiter/<int:id>', buyViews.buy_begleiter, name="buy_begleiter")
]

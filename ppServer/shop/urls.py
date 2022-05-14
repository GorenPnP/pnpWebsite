from django.urls import path

from . import views

app_name = 'shop'

urlpatterns = [
    path('', views.index, name='index'),
    path('review', views.review_items, name='review_items'),

    path('items', views.item, name='items'),
    path('waffen_werkzeuge', views.waffen_werkzeuge, name='waffen_werkzeuge'),
    path('magazine', views.magazine, name='magazine'),
    path('pfeile_bolzen', views.pfeile_bolzen, name='pfeile_bolzen'),
    path("schusswaffen", views.schusswaffen, name='schusswaffen'),
    path('mag_ausruestung', views.mag_ausrüstung, name='mag_ausrüstung'),
    path('rituale_runen', views.rituale_runen, name='rituale_runen'),
    path('ruestungen', views.rüstungen, name='rüstungen'),
    path('ausruestung_technik', views.ausrüstung_technik, name='ausr_technik'),
    path('fahrzeuge', views.fahrzeuge, name='fahrzeuge'),
    path('einbauten', views.einbauten, name='einbauten'),
    path('zauber', views.zauber, name='zauber'),
    path('vergessene_zauber', views.vergessene_zauber, name='vergessene_zauber'),
    path('alchemie', views.alchemie, name='alchemie'),
    path('tinker', views.tinker, name='tinker'),

    path('buy_item/<int:id>', views.buy_item, name="buy_item"),
    path('buy_waffen_werkzeuge/<int:id>', views.buy_waffen_werkzeuge, name="buy_waffen_werkzeuge"),
    path('buy_magazine/<int:id>', views.buy_magazin, name="buy_magazine"),
    path('buy_pfeile_bolzen/<int:id>', views.buy_pfeil_bolzen, name="buy_pfeil_bolzen"),
    path('buy_schusswaffen/<int:id>', views.buy_schusswaffe, name="buy_schusswaffen"),
    path('buy_mag_ausruestung/<int:id>', views.buy_mag_ausrüstung, name="buy_mag_ausrüstung"),
    path('buy_rituale_runen/<int:id>', views.buy_rituale_runen, name='buy_rituale_runen'),
    path('buy_ruestungen/<int:id>', views.buy_rüstung, name="buy_rüstungen"),
    path('buy_ausruestung_technik/<int:id>', views.buy_ausrüstung_technik, name="buy_ausrüstung_technik"),
    path('buy_fahrzeuge/<int:id>', views.buy_fahrzeug, name="buy_fahrzeug"),
    path('buy_einbauten/<int:id>', views.buy_einbauten, name="buy_einbauten"),
    path('buy_zauber/<int:id>', views.buy_zauber, name="buy_zauber"),
    path('buy_vergessener_zauber/<int:id>', views.buy_vergessener_zauber, name="buy_vergessener_zauber"),
    path('buy_alchemie/<int:id>', views.buy_alchemie, name="buy_alchemie")
]

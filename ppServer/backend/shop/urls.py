from django.urls import path, register_converter

from .converter import *
from .models import *
from .views.index import index, review_items, transfer_items, propose_item, shopmodel_list
from .views.detail import DetailView
from .views.list import AllListView, ListView, FernkampfwaffeView, shop_model_filter_fields

app_name = 'shop'
register_converter(get_ModelNameConverter(app_name, shopmodel_list), "model")

urlpatterns = [
    path('', index, name='index'),
    path('review/', review_items, name='review_items'),
    path('transfer-items/', transfer_items, name='transfer_items'),
    path('propose/<model:model>/', propose_item, name="propose"),

    path('all/', AllListView.as_view(), name='all'),

    path('nahkampf_wurfwaffen/', ListView.as_view(model=Nahkampfwaffe, filterset_fields={**shop_model_filter_fields, "schaden": ["gte"], "schadensart": ["exact"], "dk": ["lte"]}), name='nahkampfwaffe_list'),
    path("fernkampfwaffen", FernkampfwaffeView.as_view(), name='fernkampfwaffe_list'),
    path('rüstungen/', ListView.as_view(model=Rüstung, filterset_fields={**shop_model_filter_fields, "schutz": ["icontains"], "haltbarkeit": ["gte"]}), name='rüstung_list'),
    path('fahrzeuge/', ListView.as_view(model=Fahrzeug, filterset_fields={**shop_model_filter_fields, "geschwindigkeit": ["gte"], "hp": ["gte"], "erfolge": ["lte"]}), name='fahrzeug_list'),
    path('einbauten/', ListView.as_view(model=Einbaute, filterset_fields={**shop_model_filter_fields, "manifestverlust": ["icontains"]}), name='einbaute_list'),
    path('zauber/', ListView.as_view(model=Zauber, filterset_fields={**shop_model_filter_fields, "astralschaden": ["icontains"], "manaverbrauch": ["icontains"], "verteidigung": ["exact"], "kategorie": ["exact"], "schadensart": ["exact"]}), name='zauber_list'),
    path('engelsroboter/', ListView.as_view(model=Engelsroboter, filterset_fields={ **shop_model_filter_fields, 'ST': ["gte"], 'UM': ["gte"], 'MA': ["gte"], 'IN': ["gte"]}), name='engelsroboter_list'),
    path('<model:model>/', ListView.as_view(), name="list"),
    
    path('<model:model>/<int:id>/', DetailView.as_view(), name="detail"),
]

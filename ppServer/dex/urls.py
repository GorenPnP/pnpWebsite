from django.urls import path
from django.views.generic.base import TemplateView

from . import views, views_sp

app_name = 'dex'

urlpatterns = [
    path('', TemplateView.as_view(template_name="dex/index.html"), name='index'),

    path('monster', views.MonsterIndexView.as_view(), name='monster_index'),
    path('monster/<int:pk>', views.MonsterDetailView.as_view(), name='monster_detail'),

    path('attack', views.AttackIndexView.as_view(), name='attack_index'),
    path('type', views.TypeTableView.as_view(), name='type_table'),

    path('sp/visibility', views_sp.MonsterVisibilityView.as_view(), name='sp_monster_visibility'),
    
]

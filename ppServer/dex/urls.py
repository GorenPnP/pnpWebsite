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
    path('fähigkeit', views.MonsterFähigkeitView.as_view(), name='monster_fähigkeit_index'),

    path('monster/farm', views.MonsterFarmView.as_view(), name='monster_farm'),
    path('monster/farm/<int:pk>', views.MonsterFarmDetailView.as_view(), name='monster_detail_farm'),
    path('monster/farm/<int:pk>/levelup', views.MonsterFarmLevelupView.as_view(), name='monster_farm_levelup'),
    path('monster/team', views.MonsterTeamView.as_view(), name='monster_team'),
    path('monster/team/<int:pk>', views.MonsterTeamDetailView.as_view(), name='monster_team_detail'),
    
    # utils
    path('monster/farm/<int:pk>/new_attack', views.add_attack_to_spielermonster, name='spieler_monster_add_attack'),
    path('monster/farm/<int:pk>/new_team', views.add_team_to_spielermonster, name='spieler_monster_add_team'),
    path('monster/farm/<int:pk>/set_training', views.set_training_of_spielermonster, name='spieler_monster_set_training'),
    path('monster/farm/<int:pk>/delete_attack', views.delete_attack_from_spielermonster, name='spieler_monster_delete_attack'),
    path('monster/team/<int:pk>/new_monster', views.add_monster_to_team, name='monster_team_add_monster'),
    path('monster/team/<int:pk>/delete_monster', views.delete_monster_from_team, name='monster_team_delete_monster'),

    path('sp/visibility', views_sp.MonsterVisibilityView.as_view(), name='sp_monster_visibility'),
    
]

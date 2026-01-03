from django.urls import path

from . import views, views_sp

urlpatterns = [
    path('', views.MonsterIndexView.as_view(), name='monster_index'),
    path('<int:pk>', views.MonsterDetailView.as_view(), name='monster_detail'),

    path('attack', views.AttackIndexView.as_view(), name='attack_index'),
    path('type', views.TypeTableView.as_view(), name='type_table'),
    path('fähigkeit', views.MonsterFähigkeitView.as_view(), name='monster_fähigkeit_index'),
    path('status-effekt', views.StatusEffektView.as_view(), name='monster_statuseffekt_index'),

    path('farm', views.MonsterFarmView.as_view(), name='monster_farm'),
    path('farm/<int:pk>', views.MonsterFarmDetailView.as_view(), name='monster_detail_farm'),
    path('farm/<int:pk>/levelup', views.MonsterFarmLevelupView.as_view(), name='monster_farm_levelup'),
    path('team', views.MonsterTeamView.as_view(), name='monster_team'),
    path('team/<int:pk>', views.MonsterTeamDetailView.as_view(), name='monster_team_detail'),
    
    # utils
    path('farm/delete', views.delete_spielermonster, name='spieler_monster_delete'),
    path('farm/<int:pk>/new_attack', views.add_attack_to_spielermonster, name='spieler_monster_add_attack'),
    path('farm/<int:pk>/new_team', views.add_team_to_spielermonster, name='spieler_monster_add_team'),
    path('farm/<int:pk>/set_training', views.set_training_of_spielermonster, name='spieler_monster_set_training'),
    path('farm/<int:pk>/delete_attack', views.delete_attack_from_spielermonster, name='spieler_monster_delete_attack'),
    path('farm/<int:pk>/evolve', views.evolve_spielermonster, name='spieler_monster_evolve'),
    path('team/<int:pk>/new_monster', views.add_monster_to_team, name='monster_team_add_monster'),
    path('team/<int:pk>/delete_monster', views.delete_monster_from_team, name='monster_team_delete_monster'),

    path('attack/proposal', views.AttackProposalView.as_view(), name='attack_proposal'),
    path('attack/proposal/<int:pk>', views.AttackProposalView.as_view(), name='attack_proposal'),
    path('sp/visibility', views_sp.MonsterVisibilityView.as_view(), name='sp_monster_visibility'),
    path('sp/attack_to_monster/<int:pk>', views_sp.AttackToMonsterView.as_view(), name='sp_attack_to_monster'),
    
]

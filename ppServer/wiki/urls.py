from django.urls import path

from . import views

app_name = 'wiki'

urlpatterns = [
    path('', views.index, name='index'),
    path('vorteil', views.VorteilView.as_view(), name='vorteile'),
    path('nachteil', views.NachteilView.as_view(), name='nachteile'),
    path('talente', views.TalentView.as_view(), name='talente'),


    path('gfs', views.GfsView.as_view(), name='gfs'),
    path('gfs/special-abilities', views.GfsSpecialAbilities.as_view(), name='gfs-special-abilities'),
    path('gfs/<int:gfs_id>', views.stufenplan, name='stufenplan'),
    path('persönlichkeiten', views.PersönlichkeitTableView.as_view(), name='persönlichkeiten'),
    path('profession', views.ProfessionView.as_view(), name='profession'),
    path('profession/<int:profession_id>', views.stufenplan_profession, name='stufenplan_profession'),

    path('spezial', views.SpezialfertigkeitTableView.as_view(), name='spezial'),
    path('wissen', views.WissensfertigkeitTableView.as_view(), name='wissen'),
    path('wesenkraft', views.WesenkraftTableView.as_view(), name='wesenkraft'),

    path('berufe', views.BerufTableView.as_view(), name='berufe'),
    path('religionen', views.ReligionTableView.as_view(), name='religionen'),

    path('rangRanking', views.RangRankingTableView.as_view(), name='rangRanking'),
    path('geburtstage', views.geburtstage, name='geburtstage'),
]

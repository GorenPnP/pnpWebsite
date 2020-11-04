from django.urls import path

from . import views

app_name = 'wiki'

urlpatterns = [
    path('', views.index, name='index'),
    path('vorteil', views.vorteile, name='vorteile'),
    path('nachteil', views.nachteile, name='nachteile'),
    path('talente', views.talente, name='talente'),


    path('gfs', views.gfs, name='gfs'),
    path('gfs/<int:gfs_id>', views.stufenplan, name='stufenplan'),
    path('profession', views.profession, name='profession'),
    path('profession/<int:profession_id>', views.stufenplan_profession, name='stufenplan_profession'),

    path('spezial', views.spezial, name='spezial'),
    path('wissen', views.wissen, name='wissen'),
    path('wesenkraft', views.wesenkräfte, name='wesenkraft'),

    path('berufe', views.beruf, name='berufe'),
    path('religionen', views.religion, name='religionen'),

    path('skilltreeWesen', views.skilltreeWesen, name='skillWesen'),
    path('skilltreeRest', views.skilltreeRest, name='skillRest'),
    path('rangRanking', views.rang_ranking, name='rangRanking'),

    path('geburtstage', views.geburtstage, name='geburtstage'),
]

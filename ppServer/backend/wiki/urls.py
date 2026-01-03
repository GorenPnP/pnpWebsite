from django.urls import path

from . import views

app_name = 'wiki'

urlpatterns = [
    path('', views.index, name='index'),
    path('vorteil/', views.VorteilView.as_view(), name='vorteile'),
    path('nachteil/', views.NachteilView.as_view(), name='nachteile'),
    path('talente/', views.TalentView.as_view(), name='talente'),


    path('klassen/', views.KlasseListView.as_view(), name='klassen'),
    path('klassen/<int:pk>', views.KlasseDetailView.as_view(), name='klasse'),
    path('gfs/', views.GfsView.as_view(), name='gfs'),
    path('wesen/', views.WesenView.as_view(), name='wesen'),
    path('gfs/special-abilities/', views.GfsSpecialAbilities.as_view(), name='gfs-special-abilities'),
    path('gfs/<int:gfs_id>/', views.stufenplan, name='stufenplan'),
    path('persönlichkeiten/', views.PersönlichkeitTableView.as_view(), name='persönlichkeiten'),

    path('spezial/', views.SpezialfertigkeitTableView.as_view(), name='spezial'),
    path('wissen/', views.WissensfertigkeitTableView.as_view(), name='wissen'),
    path('wesenkraft/', views.WesenkraftTableView.as_view(), name='wesenkraft'),

    path('berufe/', views.BerufTableView.as_view(), name='berufe'),
    path('berufe/add', views.BerufAddView.as_view(), name='beruf_add'),
    path('religionen/', views.ReligionTableView.as_view(), name='religionen'),
    path('religionen/add', views.ReligionAddView.as_view(), name='religion_add'),

    path('geburtstage/', views.GeburtstageView.as_view(), name='geburtstage'),

    path('regeln/', views.RuleListView.as_view(), name='rule_index'),
    path('regeln/<int:pk>/', views.RuleDetailView.as_view(), name='rule_detail'),
]

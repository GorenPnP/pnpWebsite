from django.urls import path

from . import views
from . import views_sp

app_name = 'campaign'

urlpatterns = [
	path('auswertung', views_sp.AuswertungListView.as_view(), name='auswertung_hub'),
	path('auswertung/<int:pk>', views_sp.AuswertungView.as_view(), name='auswertung'),

	path('hub/<int:pk>', views.HubView.as_view(), name='hub'),
	path('hub/<int:pk>/attribute', views.HubAttributeView.as_view(), name='hub_attribute'),
	path('hub/<int:pk>/fertigkeiten', views.HubFertigkeitenView.as_view(), name='hub_fertigkeiten'),
	path('hub/<int:pk>/zauber', views.HubZauberView.as_view(), name='hub_zauber'),

	path('hub/<int:pk>/personal', views.HubPersonalView.as_view(), name='hub_personal'),
	path('hub/<int:pk>/vorteile', views.HubVorteileView.as_view(), name='hub_vorteile'),
	path('hub/<int:pk>/nachteile', views.HubNachteileView.as_view(), name='hub_nachteile'),
	path('hub/<int:pk>/spF_wF', views.HubSpFwFView.as_view(), name='hub_spF_wF'),
	path('hub/<int:pk>/talent', views.HubTalentView.as_view(), name='hub_talent'),
	path('hub/<int:pk>/wesenkraft', views.HubWesenkraftView.as_view(), name='hub_wesenkraft'),
	path('hub/<int:pk>/affektivität', views.HubAffektivitätView.as_view(), name='hub_affektivität'),
	path('hub/<int:pk>/skilltree', views.HubSkilltreeView.as_view(), name='hub_skilltree'),
	path('hub/<int:pk>/gfs_ability', views.HubGfsAbilityView.as_view(), name='hub_gfs_ability'),
	
	path('<int:pk>', views.HubView.as_view(), name='hub'),
]

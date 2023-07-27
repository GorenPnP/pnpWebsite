from django.urls import path

from .views.index import IndexView
from .views.attribut import GenericAttributView
from .views.fertigkeit import GenericFertigkeitView
from .views.zauber import GenericZauberView
from .views.personal import GenericPersonalView
from .views.teils import GenericVorteilView, GenericNachteilView
from .views.spF_wF import GenericSpF_wFView
from .views.talent import GenericTalentView
from .views.wesenkraft import GenericWesenkraftView
from .views.affektivität import AffektivitätView
from .views.skilltree import GenericSkilltreeView
from .views.gfs_ability import GenericGfsAbilityView

app_name = 'levelUp'

urlpatterns = [
    path('<int:pk>', IndexView.as_view(), name='index'),
	path('<int:pk>/attribute', GenericAttributView.as_view(), name='attribute'),
	path('<int:pk>/fertigkeiten', GenericFertigkeitView.as_view(), name='fertigkeiten'),
	path('<int:pk>/zauber', GenericZauberView.as_view(), name='zauber'),
	path('<int:pk>/personal', GenericPersonalView.as_view(), name='personal'),
	path('<int:pk>/vorteile', GenericVorteilView.as_view(), name='vorteile'),
	path('<int:pk>/nachteile', GenericNachteilView.as_view(), name='nachteile'),
	path('<int:pk>/spF_wF', GenericSpF_wFView.as_view(), name='spF_wF'),
	path('<int:pk>/talent', GenericTalentView.as_view(), name='talent'),
	path('<int:pk>/wesenkraft', GenericWesenkraftView.as_view(), name='wesenkraft'),
	path('<int:pk>/affektivität', AffektivitätView.as_view(), name='affektivität'),
	path('<int:pk>/skilltree', GenericSkilltreeView.as_view(), name='skilltree'),
	path('<int:pk>/gfs_ability', GenericGfsAbilityView.as_view(), name='gfs_ability'),
]
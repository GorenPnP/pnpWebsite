from django.views.decorators.csrf import csrf_protect
from django.urls import path

from . import views

app_name = 'create'

urlpatterns = [
        path('hub', views.LandingPageView.as_view(), name='landing_page'),
        path('', csrf_protect(views.GfsFormView.as_view()), name='gfs'),
        path('priotable', csrf_protect(views.PriotableFormView.as_view()), name='prio'),
        path('personal', views.PersonalFormView.as_view(), name='personal'),
        path('ap', views.ApFormView.as_view(), name='ap'),
        path('fert', views.FertigkeitFormView.as_view(), name='fert'),
        path('spF_wF', views.SpF_wFFormView.as_view(), name='spF_wF'),
        path('zauber', views.ZauberFormView.as_view(), name='zauber'),

        path('vor_nachteil', views.TeilFormView.as_view(), name='vor_nachteil'),
        path('gfs_characterization', views.GfsWahlfilterView.as_view(), name='gfs_characterization'),
]

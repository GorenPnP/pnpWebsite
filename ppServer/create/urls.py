from django.urls import path

from . import views

app_name = 'create'

urlpatterns = [
        path('', views.landing_page, name='landing_page'),
        path('gfs', views.new_gfs, name='gfs'),
        path('gfs_characterization', views.new_gfs_characterization, name='gfs_characterization'),
        path('priotable', views.new_priotable, name='prio'),
        path('ap', views.new_ap, name='ap'),
        path('fert', views.new_fert, name='fert'),
        path('zauber', views.new_zauber, name='zauber'),
        path('cp', views.new_cp, name='cp'),

        path('vor_nachteil', views.new_vor_nachteil, name='vor_nachteil'),
]

from django.urls import path

from . import views

app_name = 'politics'

urlpatterns = [
    path('plenum/', views.PlenumOverview.as_view(), name='plenum'),
    path('programs/', views.ProgramsListview.as_view(), name='party-programs'),
    path('admin/duplicate_politicians', views.AdminDuplicatePoliticiansFormview.as_view(), name='admin-duplicate-politicians'),
    path('admin/vote_on_legalAct/<int:pk>', views.VoteOnLegalActFormview.as_view(), name='admin-vote-on-legalAct'),
]

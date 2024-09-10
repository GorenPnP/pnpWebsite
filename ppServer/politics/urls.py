from django.urls import path

from . import views

app_name = 'politics'

urlpatterns = [
    path('plenum/', views.PlenumOverview.as_view(), name='plenum'),
    path('admin/duplicate_politicians', views.AdminDuplicatePoliticiansFormview.as_view(), name='admin-duplicate-politicians'),
]

from django.urls import path
from django.views.generic import TemplateView

from . import views

app_name = 'combat'

urlpatterns = [
	path('', views.RegionSelectView.as_view(), name='region_select'),
	path('region_editor/<int:pk>/', views.RegionEditorView.as_view(), name='region_editor'),
	path('fight/<int:pk>/', views.FightView.as_view(), name='fight'),
]

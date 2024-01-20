from django.urls import include, path
from django.views.generic.base import TemplateView

from . import views

app_name = 'dex'

urlpatterns = [
    path('', TemplateView.as_view(template_name="dex/index.html"), name='index'),

    path('monster/', include('dex.monster.urls')),

    path('geschöpf/', views.GeschöpfIndexView.as_view(), name='geschöpf_index'),
    path('geschöpf/<int:pk>', views.GeschöpfDetailView.as_view(), name='geschöpf_detail'),

    path('para_pflanze/', views.ParaPflanzeIndexView.as_view(), name='para_pflanze_index'),
    path('para_pflanze/<int:pk>', views.ParaPflanzeDetailView.as_view(), name='para_pflanze_detail'),

    path('para_tier/', views.ParaTierIndexView.as_view(), name='para_tier_index'),
    path('para_tier/<int:pk>', views.ParaTierDetailView.as_view(), name='para_tier_detail'),
]

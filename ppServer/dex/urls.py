from django.urls import include, path
from django.views.generic.base import TemplateView

from . import views

app_name = 'dex'

urlpatterns = [
    path('', TemplateView.as_view(template_name="dex/index.html"), name='index'),

    path('monster/', include('dex.monster.urls')),

    path('geschöpf/', views.GeschöpfIndexView.as_view(), name='geschöpf_index'),
    path('geschöpf/<int:pk>', views.GeschöpfDetailView.as_view(), name='geschöpf_detail'),
]

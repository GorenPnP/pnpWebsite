from django.urls import path
from django.views.generic.base import TemplateView

from . import views

app_name = 'dex'

urlpatterns = [
    path('', TemplateView.as_view(template_name="dex/index.html"), name='index'),

    path('monster', views.MonsterIndexView.as_view(), name='monster_index'),
    path('monster/<int:pk>', views.MonsterDetailView.as_view(), name='monster_detail'),
]

from django.urls import include, path
from django.views.generic.base import TemplateView

# from .monster import views as monster, views_sp as monster_sp

app_name = 'dex'

urlpatterns = [
    path('', TemplateView.as_view(template_name="dex/index.html"), name='index'),

    path('monster/', include('dex.monster.urls')),
]

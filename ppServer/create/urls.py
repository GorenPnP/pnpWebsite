from django.views.decorators.csrf import csrf_protect
from django.urls import path

from . import views

app_name = 'create'

urlpatterns = [
        path('gfs_characterization', views.GfsWahlfilterView.as_view(), name='gfs_characterization'),

        path('', csrf_protect(views.GfsFormView.as_view()), name='gfs'),
        path('<int:pk>/priotable', csrf_protect(views.PriotableFormView.as_view()), name='prio'),
]

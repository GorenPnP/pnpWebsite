from django.urls import path

from .views import *

app_name = 'base'

urlpatterns = [
    path('', index, name='index'),

    # for testing only
    path("redirect", redirect),
]

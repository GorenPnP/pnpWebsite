from django.urls import path

from create import views
from .views import *

app_name = 'character'

urlpatterns = [
    path('', index, name='index'),
    path('<int:pk>/', show, name='show'),
]

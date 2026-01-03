from django.urls import path

from . import views

app_name = 'changelog'

urlpatterns = [
    path('', views.ChangelogListView.as_view(), name='index'),
]

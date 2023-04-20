from django.urls import path
from . import views

app_name = 'file'

urlpatterns = [

    path('', views.TopicListView.as_view(), name='index'),
    path('<int:pk>/', views.TopicDetailView.as_view(), name='map'),
]

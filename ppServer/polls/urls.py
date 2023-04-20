from django.urls import path
from . import views

app_name = 'polls'

urlpatterns = [
    path('<int:pk>/', views.PollView.as_view(), name='detail'),
    path('<int:pk>/results/', views.ResultView.as_view(), name='results'),
]

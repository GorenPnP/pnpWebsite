from django.urls import path

from . import views

app_name = 'web_push'

urlpatterns = [
    path('test', views.TestView.as_view(), name='test'),
    path('subscribe_user', views.register_webpush, name='subscribe_user'),
]

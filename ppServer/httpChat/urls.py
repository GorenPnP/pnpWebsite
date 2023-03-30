from django.urls import path
from . import views

app_name = 'httpchat'

urlpatterns = [
    path('<slug:account_name>', views.ChatroomListView.as_view(), name='index'),
    path('<slug:account_name>/<slug:room_name>', views.ChatroomView.as_view(), name='chatroom')
]

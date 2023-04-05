from django.urls import path
from . import views

app_name = 'httpchat'

urlpatterns = [
    path('', views.AccountListView.as_view(), name='index'),
    path('<slug:account_name>', views.ChatroomListView.as_view(), name='account_chats'),
    path('<slug:account_name>/<int:room_id>', views.ChatroomView.as_view(), name='chatroom'),

    path('<slug:account_name>/<int:room_id>/poll', views.PollNewMessagesRestView.as_view(), name='poll'),
]

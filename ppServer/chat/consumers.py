import json

from django.shortcuts import get_object_or_404
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async

from character.models import Spieler

class ChatRoomConsumer(AsyncWebsocketConsumer):

    @database_sync_to_async
    def _db_is_spielleiter(self, user):
        return user.groups.filter(name__iexact="spielleiter").exists()

    @database_sync_to_async
    def _db_get_spieler(self, user):
        return get_object_or_404(Spieler, name=self.user.username)


    async def connect(self):
        self.user = self.scope["user"]
        self.spieler = await self._db_get_spieler(self.user)
        self.is_spielleiter = await self._db_is_spielleiter(self.user)

        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = 'chat_{}'.format(self.room_name)

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)

        await self.accept()

        await self.channel_layer.group_send(self.room_group_name, {
            'type': 'enter_chatroom_message',
            'username': self.user.username,
            'message': 'connected'
        })


    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

        await self.channel_layer.group_send(self.room_group_name, {
            'type': 'leave_chatroom_message',
            'username': self.user.username,
            'message': 'disconnected'
        })


    async def receive(self, text_data):
        message_text = json.loads(text_data)['message']
        charactername = json.loads(text_data)['charactername']

        await self.channel_layer.group_send(self.room_group_name,
            {
                'type': 'chatroom_message',
                'message': message_text,
                'username': self.user.username,
                'charactername': charactername,
            }
        )

    
    async def enter_chatroom_message(self, event):
        message = event['message']
        username = event['username']
        await self.send(text_data=json.dumps({
            'type': 'info',
            'message': message,
            'username': username,
        }))

    async def leave_chatroom_message(self, event):
        message = event['message']
        username = event['username']
        await self.send(text_data=json.dumps({
            'type': 'info',
            'message': message,
            'username': username,
        }))

    async def chatroom_message(self, event):
        message = event['message']
        username = event['username']
        charactername = event['charactername']

        await self.send(text_data=json.dumps({
            'type': 'message',
            'message': message,
            'username': username,
            'charactername': charactername
        }))
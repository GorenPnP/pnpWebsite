import json

from channels.generic.websocket import AsyncWebsocketConsumer

class ChatRoomConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = 'chat_{}'.format(self.room_name)

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)

        await self.accept()

        await self.channel_layer.group_send(self.room_group_name, {
            'type': 'init_chatroom_message',
            'message': 'test message on connect or chatroom init'
        })

    


    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)


    async def receive(self, text_data):
        message_text = json.loads(text_data)['message']
        username = json.loads(text_data)['name']

        await self.channel_layer.group_send(self.room_group_name,
            {
                'type': 'chatroom_message',
                'message': message_text,
                'username': username,
            }
        )

    
    async def init_chatroom_message(self, event):
        message = event['message']
        await self.send(text_data=json.dumps({'message': message}))


    async def chatroom_message(self, event):
        message = event['message']
        username = event['username']

        await self.send(text_data=json.dumps({
            'message': message,
            'username': username,
        }))
import json
from random import choice

from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async

from character.models import Spieler
from crafting.models import RelCrafting, InventoryItem
from .models import *

class MiningGameConsumer(AsyncWebsocketConsumer):

    @database_sync_to_async
    def _db_is_spielleiter(self, user):
        return user.groups.filter(name__iexact="spielleiter").exists()

    @database_sync_to_async
    def _db_get_spieler(self, user):
        return Spieler.objects.get(name=self.user.username)

    @database_sync_to_async
    def _db_get_profile(self, spieler):
        return RelCrafting.objects.get(spieler=spieler).profil

    @database_sync_to_async
    def _db_get_region(self, region_id):
        return Region.objects.get(id=region_id)

    @database_sync_to_async
    def _db_delete_entity(self, entity_id):
        return ProfileEntity.objects.get(entity__id=entity_id, profil=self.profile).delete()

    @database_sync_to_async
    def _db_add_random_loot_of(self, entity_id):
        material = Entity.objects.get(id=entity_id).material
        drops = MaterialDrop.objects.filter(material=material)
        if (len(drops) == 0): return

        loot = choice(MaterialDrop.objects.filter(material=material))
        iitem, _ = InventoryItem.objects.get_or_create(char=self.profile, item=loot.item)
        iitem.num += choice(json.loads(loot.amount))
        iitem.save()


    async def connect(self):
        self.user = self.scope["user"]
        self.spieler = await self._db_get_spieler(self.user)
        self.profile = await self._db_get_profile(self.spieler)
        # self.is_spielleiter = await self._db_is_spielleiter(self.user)

        region_id = self.scope['url_route']['kwargs']['region_id']
        self.region = await self._db_get_region(region_id)

        self.room_group_name = 'mining_game_{}_{}'.format(self.region.id, self.profile.name)

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)

        await self.accept()

        await self.channel_layer.group_send(self.room_group_name, {
            'type': 'enter_message',
            'username': self.user.username,
            'message': 'connected'
        })


    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

        await self.channel_layer.group_send(self.room_group_name, {
            'type': 'leave_message',
            'username': self.user.username,
            'message': 'disconnected'
        })


    async def receive(self, text_data):
        type = json.loads(text_data)['type']
        entity_id = json.loads(text_data)['message']

        await self.channel_layer.group_send(self.room_group_name,
            {
                'type': type,
                'message': entity_id,
                'username': self.user.username
            }
        )

    async def break_entity_message(self, event):
        entity_id = event['message']

        # add loot
        await self._db_add_random_loot_of(entity_id)

        # remove entity
        await self._db_delete_entity(entity_id)

        # send message
        username = event['username']
        await self.send(text_data=json.dumps({
            'type': 'break_entity_message',
            'message': entity_id,
            'username': username,
        }))

    
    async def enter_message(self, event):
        message = event['message']
        username = event['username']
        await self.send(text_data=json.dumps({
            'type': 'info',
            'message': message,
            'username': username
        }))

    async def leave_message(self, event):
        message = event['message']
        username = event['username']

        await self.send(text_data=json.dumps({
            'type': 'info',
            'message': message,
            'username': username,
        }))

        # multiple windows of same user open? cut all connections to THIS CHAT on logout
        if username == self.spieler.name:
            self.close()
            self.disconnect(None)

import json
from random import choice
from asgiref.sync import sync_to_async

from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async

from character.models import Spieler
from crafting.models import RelCrafting
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
        return ProfileEntity.objects.filter(entity__id=entity_id, profil=self.profile).delete()

    @database_sync_to_async
    def _db_add_random_loot_of(self, entity_id):

        # get possible drops
        material = Entity.objects.get(id=entity_id).material
        drops = MaterialDrop.objects.filter(material=material)
        if (len(drops) == 0): return

        loot = choice(MaterialDrop.objects.filter(material=material))
        if loot.amount == 0:
            return 0, None

        # get inventory
        rel_profile, _ = RelProfile.objects.get_or_create(profile=self.profile, spieler=self.spieler)
        if rel_profile.inventory is None:
            inventory = Inventory.objects.create()
            rel_profile.inventory = inventory
            rel_profile.save(update_fields=["inventory"])

        # get inventory item
        iitems = InventoryItem.objects.filter(inventory=rel_profile.inventory, item__crafting_item=loot.item)
        if not len(iitems):
            item, _ = Item.objects.get_or_create(crafting_item=loot.item)
            iitem = InventoryItem.objects.create(inventory=rel_profile.inventory, item=item)
        else:
            iitem = iitems[0]

        # add amount to inventpry item
        amount = choice(json.loads(loot.amount))
        iitem.amount += amount

        iitem.save(update_fields=["amount"])

        # return loot
        return amount, iitem

    @database_sync_to_async
    def _db_get_item_dict_of_inventory_item(self, iitem):
        return Item.objects.get(id=iitem.item_id).toDict()

    @database_sync_to_async
    def _db_save_player_position(self, position):
        print("save {} of {}".format(position, self.user.username))
        return


    @database_sync_to_async
    def _db_save_inventory_item(self, inventory_item):

        # prepare
        item = Item.objects.get(id=inventory_item["item_id"])
        inventory = Inventory.objects.get(id=inventory_item["inventory_id"])

        # get iitem
        if "id" in inventory_item.keys() and inventory_item["id"]:
            iitem, _ = InventoryItem.objects.get_or_create(id=inventory_item["id"])
        else:
            iitem = InventoryItem.objects.create(inventory=inventory, item=item)

        # set its properties
        iitem.item = item
        iitem.inventory = inventory
        iitem.position = {"x": inventory_item["x"], "y": inventory_item["y"]}
        iitem.rotated = inventory_item["rotated"]
        iitem.amount = inventory_item["amount"]

        iitem.save(update_fields=["item", "inventory", "position", "rotated", "amount"])
        return iitem


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
        message = json.loads(text_data)['message']

        if type == "save_player_position_message":
            return await self._db_save_player_position(json.loads(text_data)['message'])
        if type == "save_inventory_item_message":
            saved_iitem = await self._db_save_inventory_item(json.loads(text_data)['message'])
            message = saved_iitem.id

        await self.channel_layer.group_send(self.room_group_name,
            {
                'type': type,
                'message': message,
                'username': self.user.username
            }
        )

    async def break_entity_message(self, event):
        entity_id = event['message']

        # add loot
        loot = await self._db_add_random_loot_of(entity_id)
        amount = loot[0]
        iitem = loot[1]
        item_dict = None
        if amount:
            item_dict = await self._db_get_item_dict_of_inventory_item(iitem)

            # remove entity
            await self._db_delete_entity(entity_id)

        # send message
        username = event['username']
        await self.send(text_data=json.dumps({
            'type': 'break_entity_message',
            'message': {"entity_id": entity_id, "amount": amount, "total_amount": iitem.amount if amount else None, "item": item_dict if item_dict else None},
            'username': username,
        }))

    
    async def player_position_message(self, event):
        position_and_speed = event['message']

        # send message
        username = event['username']
        await self.send(text_data=json.dumps({
            'type': 'player_position_message',
            'message': position_and_speed,
            'username': username,
        }))
    
    async def save_inventory_item_message(self, event):
        iitem_id = event['message']

        # send message
        username = event['username']
        await self.send(text_data=json.dumps({
            'type': 'save_inventory_item_message',
            'message': iitem_id,
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

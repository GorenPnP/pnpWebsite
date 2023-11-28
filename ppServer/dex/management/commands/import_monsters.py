import requests, urllib
from datetime import datetime, timedelta
from django.utils.timezone import now

from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User

from dex.models import Typ, Dice, Attacke, Monster



class Command(BaseCommand):
    help = "imports all monsters, their attacks & types from pnp.eu.pythonanywhere.com into the db"

    def handle(self, *args, **options):
        self._import_types()
        # self._import_attacks()
        # self._import_monsters()



    def _import_types(self):
        # TYPES
        params = { "query": "query{type{id,name}}" }

        types = requests.get("https://pnp.eu.pythonanywhere.com", params).json()["type"]
        for type in types:
            Typ.objects.get_or_create(id=type["id"], defaults={"name": type["name"]})

        self.stdout.write(self.style.SUCCESS(f'Successfully imported {len(types)} Types'))

        # TYPE EFFICIENCIES
        params = { "query": "query{typeEfficiency{fromType,toType,efficiency}}" }

        efficiencies = {t.id: {"VERY_EFFECTIVE" : [], "NOT_EFFECTIVE": [], "DOES_NOT_HIT": []} for t in Typ.objects.all()}
        for eff in requests.get("https://pnp.eu.pythonanywhere.com", params).json()["typeEfficiency"]:
            efficiencies[int(eff["fromType"])][eff["efficiency"]].append(int(eff["toType"]))

        print(efficiencies)
        for type_id, effs in efficiencies.items():
            type_object = Typ.objects.get(id=int(type_id))

            type_object.stark_gegen.set(effs["VERY_EFFECTIVE"])
            type_object.schwach_gegen.set(effs["NOT_EFFECTIVE"])
            type_object.trifft_nicht.set(effs["DOES_NOT_HIT"])

        self.stdout.write(self.style.SUCCESS(f'Successfully imported TypeEfficiencies'))


    def _import_attacks(self):
        # ATTACKS
        params = { "query": "query{attack{id,name,damage,description,types{id}}}" }

        attacks = requests.get("https://pnp.eu.pythonanywhere.com", params).json()["attack"]
        for attack in attacks:
            attack_object, _ = Attacke.objects.get_or_create(id=attack["id"], defaults={
                "name": attack["name"],
                "description": attack["description"],
                "macht_schaden": "w" in attack["damage"].lower()
            })

            # attack's types
            type_ids = [int(t["id"]) for t in attack["types"]]
            attack_object.types.set(Typ.objects.filter(id__in=type_ids))

            # attack's damage
            damage_dice_data = [{"amount": int(dice.lower().split("w")[0]), "type": f"w{dice.lower().split('w')[-1]}"} for dice in attack["damage"].split("+") if "W" in dice]
            dice_objects = []
            for dice in damage_dice_data:
                dice_object, _ = Dice.objects.get_or_create(**dice)
                dice_objects.append(dice_object)
            attack_object.damage.set(dice_objects)

        self.stdout.write(self.style.SUCCESS(f'Successfully imported {len(attacks)} Attacks'))


    def _import_monsters(self):
        # MONSTER
        params = { "query": "query{monster{id,name,rank,height,hp,habitat,description,damagePrevention,weight,forms,opposite,evolutionPre,evolutionAfter,types{id},attacks{id}}}" }

        monsters = requests.get("https://pnp.eu.pythonanywhere.com", params).json()["monster"]
        for monster in monsters:
            monster_object, _ = Monster.objects.get_or_create(id=monster["id"], defaults={
                "number": monster["id"],
                "name": monster["name"],
                "description": monster["description"],
                "habitat": monster["habitat"],
                "wildrang": int(monster["rank"]),
                "weight": float(monster["weight"]),
                "height": float(monster["height"]),
                "base_hp": int(monster["hp"]),
            })

            # monster's types
            type_ids = [int(t["id"]) for t in monster["types"]]
            monster_object.types.set(Typ.objects.filter(id__in=type_ids))

            # monster's attacks
            attack_ids = [int(t["id"]) for t in monster["attacks"]]
            monster_object.attacken.set(Attacke.objects.filter(id__in=attack_ids))

            # monster's damage
            schadensWI_dice_data = [{"amount": int(dice.lower().split("w")[0]), "type": f"w{dice.lower().split('w')[-1]}"} for dice in monster["damagePrevention"].split("+") if "W" in dice]
            dice_objects = []
            for dice in schadensWI_dice_data:
                dice_object, _ = Dice.objects.get_or_create(**dice)
                dice_objects.append(dice_object)
            monster_object.base_schadensWI.set(dice_objects)

        # m2m fields: forms, opposite, evolutionPre,evolutionAfter
        for monster in monsters:
            monster_object = Monster.objects.get(number=int(monster["id"]))

            monster_object.alternativeForms.set([int(m) for m in monster["forms"]])
            monster_object.opposites.set([int(m) for m in monster["opposite"]])
            monster_object.evolutionPre.set([int(m) for m in monster["evolutionPre"]])
            monster_object.evolutionPost.set([int(m) for m in monster["evolutionAfter"]])

        self.stdout.write(self.style.SUCCESS(f'Successfully imported {len(monsters)} Monster'))
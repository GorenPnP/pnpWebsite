import json

from django.contrib import messages
from django.db.models import Subquery, F, Q
from django.db.models.functions import Coalesce
from django.http import HttpResponseNotFound
from django.http.response import JsonResponse
from django.shortcuts import redirect, get_object_or_404, reverse
from django.views.generic import DetailView
from django.views.generic.base import TemplateView
from django.views.generic.list import ListView

from ppServer.mixins import SpielleiterOnlyMixin, VerifiedAccountMixin
from ppServer.utils import ConcatSubquery
from shop.models import Tinker

from .forms import AddToInventoryForm
from .models import *
from .mixins import ProfileSetMixin
from .templatetags.crafting.duration import duration
from .utils import *


class IndexView(VerifiedAccountMixin, TemplateView):
	template_name = "crafting/index.html"

	def get_context_data(self, **kwargs):
		return super().get_context_data(
			**kwargs,
			topic = "Profilwahl",
			app_index = "Crafting",
			app_index_url = reverse("crafting:craft"),

			profiles = Profile.objects.all(),
		)
	
	def post(self, *args, **kwargs):

		name = self.request.POST.get("name")
		spieler = self.request.spieler.instance
		if not spieler: return HttpResponseNotFound()

		# get or create profile with name
		profile, created = Profile.objects.get_or_create(name=name)
		if created:
			profile.owner = spieler
			profile.restricted = self.request.POST.get("restriction") is not None
			profile.save(update_fields=["owner", "restricted"])

		# set profile as current
		rel, _ = RelCrafting.objects.get_or_create(spieler=spieler)
		rel.profil = profile
		rel.save(update_fields=["profil"])
    	
		redirect_path = self.request.GET.get("redirect")
		return redirect(redirect_path if redirect_path and redirect_path.startswith("/crafting/") else reverse("crafting:inventory"))


class InventoryView(VerifiedAccountMixin, ProfileSetMixin, DetailView):
	model = Profile
	template_name = "crafting/inventory.html"

	object = None
	def get_object(self):
		if self.object: return self.object
		spieler = self.request.spieler.instance
		if not spieler: return HttpResponseNotFound()

		rel, _ = RelCrafting.objects.prefetch_related("profil").get_or_create(spieler=spieler)
		self.object = rel.profil

		return self.object


	def get_context_data(self, **kwargs):
		self.object = self.get_object()

		return super().get_context_data(
			**kwargs,
			topic = "Inventar von {}".format(self.object.name),
			app_index = "Crafting",
			app_index_url = reverse("crafting:craft"),

			add_form = AddToInventoryForm(),
			restricted_profile = self.object.restricted,
			items = InventoryItem.objects.filter(char=self.object).order_by("item__name").prefetch_related("item"),
		)

	def post(self, *args, **kwargs):

		json_dict = json.loads(self.request.body.decode("utf-8"))

		# add item to inventory without crafting
		if "item" in json_dict.keys():

			try:
				id = int(json_dict["item"])
				num = int(json_dict["num"])
			except:
				return JsonResponse({"message": "Konnte Parameter nicht lesbar empfangen"}, status=418)

			# add num of items and save
			item = get_object_or_404(Tinker, id=id)
			iitem, _ = InventoryItem.objects.get_or_create(char=self.object, item=item)
			iitem.num += num
			iitem.save(update_fields=["num"])

			return JsonResponse({})


		# gather all the details of one item to display them
		if "details" in json_dict.keys():

			try:
				id = int(json_dict["details"])
			except:
				return JsonResponse({"message": "Konnte Parameter nicht lesbar empfangen"}, status=418)

			# get inventory item (has to exist, because clicked on it in inventory)
			iitem = get_object_or_404(InventoryItem, item__id=id, char=self.get_object())
			prod = Product.objects.filter(item=iitem.item).first()

			weiteres = "illegal" if iitem.item.illegal else ""
			if iitem.item.lizenz_benötigt and not weiteres:
					weiteres = "Lizenz benötigt"
			if iitem.item.lizenz_benötigt and iitem.item.illegal:
					weiteres += ", Lizenz benötigt"

			data = {
					"id": iitem.item.id,
					"link": "{}?name__icontains={}".format(reverse("shop:tinker"), iitem.item.name.replace(" ", "+")),
					"name": iitem.item.name,
					"table": {"name": "", "icon": ""},
					"ingredients": [],
					"icon": iitem.item.getIconUrl(),
					"description": iitem.item.beschreibung,
					"values": iitem.item.werte,
					"other": weiteres,
					"duration": "",
					"spezial": [],
					"wissen": [],
					"ab_stufe": iitem.item.ab_stufe,
					"kategory": iitem.item.get_kategorie_display(),
					"num_prod": "",
					"own": iitem.num}

			# not found
			if not prod: return JsonResponse(data)

			recipe = prod.recipe
			ingredients = recipe.ingredient_set.all()

			# iitem is not json-serializable, therefore mapping manually ...
			missing_fields = {
				"table": {"name": recipe.table.name, "icon": recipe.table.getIconUrl()} if recipe.table else Recipe.getHandwerk(),
				"ingredients": [{"icon": i.item.getIconUrl(), "name": i.item.name, "num": i.num} for i in  ingredients],
				"duration": duration(recipe.duration),
				"spezial": [e.titel for e in recipe.spezial.all()],
				"wissen": [e.titel for e in recipe.wissen.all()],
				"num_prod": prod.num}
			for k, v in missing_fields.items(): data[k] = v

			return JsonResponse(data)


class CraftingView(VerifiedAccountMixin, ProfileSetMixin, ListView):
	model = InventoryItem
	template_name = "crafting/craft.html"

	def get_queryset(self):
		return InventoryItem.objects.prefetch_related("item").filter(char=self.relCrafting.profil)

	def get_context_data(self, **kwargs):
		# collect current inventory
		self.inventory = {i.item.id: i.num for i in self.get_queryset()}

		# get all (used) table instances from db in alphabetical order
		table_list = self.relCrafting.profil.getTables()
		for t in table_list: t["available"] = t["id"] in self.inventory.keys() or t["id"] == 0		# id == 0: special case for Handwerk (is always available)

		return super().get_context_data(
			**kwargs,
			topic = table_list[0]["name"],

			tables = table_list,
			recipes = get_recipes_of_table(self.inventory, self.relCrafting.profil.restricted, table_list[0]["id"] if len(table_list) else 0),
		)


	def post(self, *args, **kwargs):
		# collect current inventory
		self.inventory = {i.item.id: i.num for i in self.get_queryset()}

		json_dict = json.loads(self.request.body.decode("utf-8"))

		# table selection has changed, update the recipes
		if "table" in json_dict.keys():
			try:
				table_id = int(json_dict["table"])
			except: return JsonResponse({"message": "Parameter nicht lesbar angekommen"}, status=418)

			return JsonResponse({"recipes": get_recipes_of_table(self.inventory, self.relCrafting.profil.restricted, table_id)})


		# search for an item, return just names for autocomplete
		if "search" in json_dict.keys():

			search = json_dict["search"]
			return JsonResponse({"res": [{"name": t.name} for t in Tinker.objects.filter(name__iregex=search) if not (self.relCrafting.profil.restricted and not TinkerNeeds.objects.filter(product=t).exists())]})


		# search for an item
		if "search_btn" in json_dict.keys():
			search = json_dict["search_btn"]

			return JsonResponse({"as_product": construct_recipes(Product.objects.filter(item__name__iregex=search), self.inventory, self.relCrafting),
                           "as_ingredient": construct_recipes(Ingredient.objects.filter(item__name__iregex=search), self.inventory, self.relCrafting)})


		# craft items out of others at a table
		if "craft" in json_dict.keys():

			try:
				id = int(json_dict["craft"])		# recipe id
				num = int(json_dict["num"])
			except:
				return JsonResponse({"message": "Parameter nicht lesbar angekommen"}, status=418)

			# get the product prototype
			recipe = get_object_or_404(Recipe, id=id)

			# test if table owned
			if recipe.table and recipe.table.id not in self.inventory.keys():
				return JsonResponse({"message": "Tisch nicht vorhanden."}, status=418)


			# test if enough ingredients exist and collect them in 'ingredients'. Keys are tinker_id's
			ingredients = {}
			for ni in recipe.ingredient_set.all():

				#  ingredient not owned. Abort.
				if not ni.item.id in self.inventory.keys(): return JsonResponse({"message": "Zu wenig Materialien vorhanden."}, status=418)

				num_owned = self.inventory[ni.item.id]
				debt = ni.num * num

				# insufficient amount of ingredients. Abort.
				if num_owned < debt: return JsonResponse({"message": "Zu wenig Materialien vorhanden."}, status=418)

				ingredients[ni.item.id] = debt		# save debt at inventoryItem id


			# subtract amounts
			for ni in InventoryItem.objects.filter(item__id__in=ingredients.keys(), char=self.relCrafting.profil):

				# decrease ingredient amount
				if ni.num == ingredients[ni.item.id]:
					ni.delete()
				else:
					ni.num -= ingredients[ni.item.id]
					ni.save(update_fields=["num"])


			# add crafting time
			if self.relCrafting.profil.craftingTime: self.relCrafting.profil.craftingTime += recipe.duration * num
			else:						self.relCrafting.profil.craftingTime  = recipe.duration * num

			self.relCrafting.profil.save(update_fields=["craftingTime"])


			# save products
			for t in recipe.product_set.all():
				crafted, _ = InventoryItem.objects.get_or_create(char=self.relCrafting.profil, item=t.item)
				crafted.num += t.num * num
				crafted.save(update_fields=["num"])

			return JsonResponse({})


		# save new ordering of tables in profile model
		if "table_ordering" in json_dict.keys():

			self.relCrafting.profil.tableOrdering = [to for to in json_dict["table_ordering"] if to is not None]
			self.relCrafting.profil.save(update_fields=["tableOrdering"])

			return JsonResponse({})


class RecipeDetailsView(VerifiedAccountMixin, ProfileSetMixin, DetailView):
	model = Recipe
	template_name = "crafting/details.html"

	def get_queryset(self):
		return super().get_queryset().prefetch_related("table", "ingredient_set__item", "product_set__item").annotate(
			spezial_names = ConcatSubquery(Spezialfertigkeit.objects.filter(recipe=self.kwargs["pk"]).values("titel"), ", "),
			wissen_names = ConcatSubquery(Wissensfertigkeit.objects.filter(recipe=self.kwargs["pk"]).values("titel"), ", "),
		)

	def get_context_data(self, **kwargs):
		return super().get_context_data(
			**kwargs,
			topic = "Rezept",
			app_index = "Crafting",
			app_index_url = reverse("crafting:craft"),

			handwerk = Recipe.getHandwerk(),
		)


class SpGiveItemsView(VerifiedAccountMixin, SpielleiterOnlyMixin, ProfileSetMixin, TemplateView):
	template_name = "crafting/sp_give_items.html"

	def get_context_data(self, **kwargs):
		return super().get_context_data(
			**kwargs,
			topic = "Profilen Items geben",
			app_index = "Crafting",
			app_index_url = reverse("crafting:craft"),

			allProfiles = sorted([{"name": p.name, "id": p.id, "restricted": p.restricted} for p in Profile.objects.all()], key=lambda p: p["name"]),
			allItems = sorted([{"icon": t.getIconUrl(), "id": t.id, "name": t.name} for t in Tinker.objects.all()], key=lambda t: t["name"]),
		)

	def post(self, *args, **kwargs):
		json_dict = json.loads(self.request.body.decode("utf-8"))

		try:
			item = int(json_dict["item"])
			profile = int(json_dict["profile"])
			num = int(json_dict["num"])
		except:
			return JsonResponse({"message": "Konnte Parameter nicht lesbar empfangen"}, status=418)

		# add num of items and save
		item = get_object_or_404(Tinker, id=item)
		profile = get_object_or_404(Profile, id=profile)

		iitem, _ = InventoryItem.objects.get_or_create(char=profile, item=item)
		iitem.num += num
		iitem.save(update_fields=["num"])

		return JsonResponse({})



class RegionListView(VerifiedAccountMixin, ProfileSetMixin, ListView):
	model = Region
	template_name = "crafting/regions.html"

	def get_queryset(self):
		return super().get_queryset().filter(allowed_profiles=self.relCrafting.profil)
	
	def get_context_data(self, **kwargs):
		drops = {region.pk: Tinker.objects.filter(drop__block__blockchance__region=region).distinct() for region in self.get_queryset()}

		return super().get_context_data(
			**kwargs,
            topic = "Regionen für {}".format(self.relCrafting.profil.name),
            app_index = "Crafting",
            app_index_url = reverse("crafting:craft"),

			drops = drops,
        )


class MiningView(VerifiedAccountMixin, ProfileSetMixin, DetailView):
	model = Region
	template_name = "crafting/mining.html"
	object = None


	def check_region_allowed(self):
		self.object = self.object or self.get_object()
		allowed = self.object.allowed_profiles.filter(id=self.relCrafting.profil.id).exists()
		if not allowed:
			messages.error(self.request, f"Kein Zutritt zur {self.object}")
			return "crafting:regions"
		return None

	def get_context_data(self, **kwargs):
		# collect mining blocks & their drops
		pool = []
		blocks = {}
		for block_chance in self.object.blockchance_set.prefetch_related("block__drop_set__item").all():
			for _ in range(block_chance.chance): pool.append(block_chance.block.pk)
			blocks[block_chance.block.pk] = block_chance.block.toDict()

		# collect tools
		tool_qs = Tool.objects.filter(item__inventoryitem__char=self.relCrafting.profil)
		tools = tool_qs.prefetch_related("item").annotate(
			pick_maxspeed = Coalesce(Subquery(tool_qs.filter(is_pick=True).values("speed")[:1]), 0),
			axe_maxspeed = Coalesce(Subquery(tool_qs.filter(is_axe=True).values("speed")[:1]), 0),
			shovel_maxspeed = Coalesce(Subquery(tool_qs.filter(is_shovel=True).values("speed")[:1]), 0),
		).filter(
			(Q(is_pick=True) & Q(speed=F("pick_maxspeed"))) |
			(Q(is_axe=True) & Q(speed=F("axe_maxspeed"))) |
			(Q(is_shovel=True) & Q(speed=F("shovel_maxspeed")))
		)

		return super().get_context_data(
			**kwargs,
            topic = "Mining von {}".format(self.relCrafting.profil.name),
            app_index = "Crafting",
            app_index_url = reverse("crafting:regions"),

            profil = self.relCrafting.profil,
            items = InventoryItem.objects.filter(char=self.relCrafting.profil).order_by("item__name").prefetch_related("item"),
			block_pool = pool,
			blocks = blocks,
			tools = [tool.toDict() for tool in tools],
        )
	
	def get(self, request, *args, **kwargs):
		redirectUrl = self.check_region_allowed()
		if redirectUrl: return redirect(redirectUrl)

		return super().get(request, *args, **kwargs)
    
	def post(self, *args, **kwargs):
		redirectUrl = self.check_region_allowed()
		if redirectUrl: return redirect(redirectUrl)

		json_dict = json.loads(self.request.body.decode("utf-8"))

		# gather all the details of one item to display them
		if "details" in json_dict:
			return InventoryView(request=self.request).post(*args, **kwargs)

		if "drops" in json_dict and "time" in json_dict:
			from datetime import datetime, timedelta
			drops = json_dict["drops"]
			time = timedelta(milliseconds=json_dict["time"])

			for tinker in Tinker.objects.filter(pk__in=[k for k, v in drops.items() if v > 0]):
				iitem, _ = InventoryItem.objects.get_or_create(char=self.relCrafting.profil, item=tinker)
				iitem.num += drops[str(tinker.pk)]
				iitem.save(update_fields=["num"])


			# add mining time
			if self.relCrafting.profil.miningTime: self.relCrafting.profil.miningTime += time
			else:						self.relCrafting.profil.miningTime  = time

			self.relCrafting.profil.save(update_fields=["miningTime"])

			return JsonResponse({})

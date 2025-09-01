import json
from datetime import timedelta

from django.contrib import messages
from django.db.models import Subquery, F, Q, Exists, OuterRef, Case, When, Count
from django.db.models.functions import Coalesce
from django.http import HttpResponseNotFound
from django.http.response import JsonResponse
from django.shortcuts import redirect, get_object_or_404, reverse
from django.views.generic import DetailView
from django.views.generic.base import TemplateView
from django.views.generic.list import ListView
from django.utils.html import format_html

from combat.models import Region as CombatRegion
from ppServer.mixins import SpielleitungOnlyMixin, VerifiedAccountMixin
from ppServer.utils import ConcatSubquery
from shop.models import Tinker
from shop.enums import tinker_enum

from .forms import AddToInventoryForm
from .models import *
from .mixins import ProfileSetMixin
from .templatetags.crafting.duration import duration
from .utils import *


def handle_overlay(json_dict: dict, item_qs: QuerySet[Tinker], profil:Profile) -> JsonResponse:

	# add item to inventory without crafting
	if "item_id" in json_dict.keys():

		try:
			num = int(json_dict["num"])
			id = int(json_dict["item_id"])
			item = get_object_or_404(item_qs, is_perk=False, id=id)
		except:
			return JsonResponse({"message": "Konnte Parameter nicht lesbar empfangen"}, status=418)

		if "buy" in json_dict.keys():

			# add num of items, pay and save
			wooble_cost = item.wooble_buy_price * num
			if wooble_cost > profil.woobles:
				return JsonResponse({"message": "Dafür hast du zu wenig Woobles :("}, status=418)

			profil.woobles -= wooble_cost
			profil.save(update_fields=["woobles"])

			iitem, _ = InventoryItem.objects.get_or_create(char=profil, item=item)
			iitem.num += num
			iitem.save(update_fields=["num"])

		elif "sell" in json_dict.keys():
			# remove num of items, get woobles and save
			iitem = get_object_or_404(InventoryItem.objects.prefetch_related("item"), item=item, char=profil)
			if iitem.num < num:
				return JsonResponse({"message": "So viele hast du nicht"}, status=418)

			iitem.num -= num
			iitem.save(update_fields=["num"])

			profil.woobles += (iitem.item.wooble_sell_price * num)
			profil.save(update_fields=["woobles"])
		
		else:
			return JsonResponse({"message": "Konnte Parameter buy/sell nicht lesbar empfangen"}, status=418)

		clean_inventory(profil)

		return JsonResponse({})

	elif "details" in json_dict:
		try:
			id = int(json_dict["details"])
		except:
			return JsonResponse({"message": "Konnte Parameter nicht lesbar empfangen"}, status=418)

		# get inventory item (has to exist, because clicked on it in inventory)
		item = get_object_or_404(item_qs, id=id)
		recipe = Recipe.objects\
			.prefetch_related("ingredient_set__item", "spezial", "wissen")\
			.filter(product__item=item)\
			.annotate(product_num = Subquery(Product.objects.filter(item=item, recipe=OuterRef("pk")).values_list("num", flat=True)[:1]))\
			.first()

		weiteres = "illegal" if item.illegal else ""
		if item.lizenz_benötigt and not weiteres:
				weiteres = "Lizenz benötigt"
		if item.lizenz_benötigt and item.illegal:
				weiteres += ", Lizenz benötigt"

		data = {
			"id": item.id,
			"link": "{}?name__icontains={}".format(reverse("shop:tinker"), item.name.replace(" ", "+")),
			"name": item.name,
			"table": {"name": "", "icon": ""},
			"ingredients": [],
			"icon": item.getIconUrl(),
			"description": item.beschreibung,
			"values": item.werte,
			"other": weiteres,
			"duration": "",
			"spezial": [],
			"wissen": [],
			"ab_stufe": item.ab_stufe,
			"kategory": item.get_kategorie_display(),
			"num_prod": "",
			"own": item.num,
			"wooble_buy": item.wooble_buy_price,
			"wooble_sell": item.wooble_sell_price,
			"is_perk": item.is_perk,
		}

		# not found
		if not recipe: return JsonResponse(data)

		# iitem is not json-serializable, therefore mapping manually ...
		missing_fields = {
			"table": {"name": recipe.table.name, "icon": recipe.table.getIconUrl()} if recipe.table else Recipe.getHandwerk(),
			"ingredients": [{"icon": i.item.getIconUrl(), "name": i.item.name, "num": i.num} for i in recipe.ingredient_set.all()],
			"duration": duration(recipe.duration),
			"spezial": [e.titel for e in recipe.spezial.all()],
			"wissen": [e.titel for e in recipe.wissen.all()],
			"num_prod": recipe.product_num,
		}
		for k, v in missing_fields.items(): data[k] = v

		return JsonResponse(data)


def clean_inventory(profile: Profile) -> None:
	InventoryItem.objects.filter(char=profile, num=0).delete()


class IndexView(VerifiedAccountMixin, TemplateView):
	template_name = "crafting/index.html"

	def get_context_data(self, **kwargs):
		relProfil, _ = RelCrafting.objects.get_or_create(spieler=self.request.spieler.instance)

		return super().get_context_data(
			**kwargs,
			topic = "Profilwahl",
			app_index = "Crafting",
			app_index_url = reverse("crafting:craft"),

			relProfil = relProfil,
			profiles = Profile.objects.all(),
			chars = Charakter.objects.filter(eigentümer=self.request.spieler.instance, in_erstellung=False)
		)
	
	def post(self, *args, **kwargs):

		name = self.request.POST.get("name")
		spieler = self.request.spieler.instance
		if not spieler: return HttpResponseNotFound()
		char = get_object_or_404(Charakter.objects.filter(eigentümer=spieler, in_erstellung=False), pk=self.request.POST.get("char"))

		# get or create profile with name
		profile, created = Profile.objects.get_or_create(name=name)
		if created:
			profile.owner = spieler
			profile.restricted = self.request.POST.get("restriction") is not None
			profile.save(update_fields=["owner", "restricted"])

		# set profile as current
		rel, _ = RelCrafting.objects.get_or_create(spieler=spieler)
		rel.profil = profile
		rel.char = char
		rel.save(update_fields=["profil", "char"])
    	
		redirect_path = self.request.GET.get("redirect")
		return redirect(redirect_path if redirect_path and (redirect_path.startswith("/crafting/") or redirect_path.startswith("/combat/")) else reverse("crafting:inventory"))


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
	
	def get_item_qs(self, filter_perks=False):
		qs = Tinker.objects.annotate(
				num = Coalesce(Subquery(InventoryItem.objects.filter(char=self.relCrafting.profil, item=OuterRef("pk")).values_list("num", flat=True)[:1]), 0.0),
				owned = Case(When(num=0, then=False), default=True, output_field=models.BooleanField()),

				is_perk = Exists(MiningPerk.objects.filter(item=OuterRef("pk"))),
			).order_by("-owned", "name")
		if filter_perks: qs = qs.filter(is_perk=False)

		return qs


	def get_context_data(self, **kwargs):
		self.object = self.get_object()

		return super().get_context_data(
			**kwargs,
			topic = "Inventar von {}".format(self.object.name),
			app_index = "Crafting",
			app_index_url = reverse("crafting:craft"),

			add_form = AddToInventoryForm(),
			restricted_profile = self.object.restricted,
			items = self.get_item_qs(),
			categories = sorted([val[1] for val in tinker_enum], key=lambda val: val.lower()),
		)

	def post(self, *args, **kwargs):

		json_dict = json.loads(self.request.body.decode("utf-8"))

		# gather all the details of one item to display them OR buy/sell items
		if "details" in json_dict.keys() or "item_id" in json_dict:
			return handle_overlay(json_dict, self.get_item_qs(), self.relCrafting.profil)


class CraftingView(VerifiedAccountMixin, ProfileSetMixin, ListView):
	model = InventoryItem
	template_name = "crafting/craft.html"

	def get_queryset(self):
		return InventoryItem.objects.prefetch_related("item").filter(char=self.relCrafting.profil)

	def get_recipe_queryset(self, set_perk_filter=True) -> QuerySet[Recipe]:
		owned_perk_items = Tinker.objects.exclude(miningperk=None).filter(inventoryitem__char=self.relCrafting.profil)
		qs = Recipe.objects.prefetch_related("ingredient_set__item", "product_set__item", "table")\
			.annotate(
				ingredient_exists = Exists(Ingredient.objects.filter(recipe=OuterRef("pk"))),
				produces_perk = Exists(MiningPerk.objects.filter(item__in=OuterRef("product__item"))),
				produces_known_perk = Exists(Product.objects.filter(recipe=OuterRef("pk"), item__in=owned_perk_items)),
				is_fav = Exists(self.relCrafting.favorite_recipes.filter(id=OuterRef("pk"))),
			)

		if self.relCrafting.profil.restricted: qs = qs.filter(ingredient_exists=True)
		if set_perk_filter: qs = qs.filter(produces_known_perk=False)

		return qs.distinct()

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
			recipes = construct_recipes(self.get_recipe_queryset(), self.inventory, table_list[0]["id"] if len(table_list) else 0),
			has_favorite_recipes = self.relCrafting.favorite_recipes.exists(),
		)


	def post(self, *args, **kwargs):
		# collect current inventory
		self.inventory = {i.item.id: i.num for i in self.get_queryset()}

		json_dict = json.loads(self.request.body.decode("utf-8"))

		# table selection has changed, update the recipes
		if "table" in json_dict.keys():
			try:
				restrict_to_fav = json_dict["table"] == "fav"
				table_id = int(json_dict["table"]) if not restrict_to_fav else None
			except:
				if not restrict_to_fav: return JsonResponse({"message": "Parameter nicht lesbar angekommen"}, status=418)

			qs = self.get_recipe_queryset()
			if restrict_to_fav:
				qs = qs.filter(pk__in=self.relCrafting.favorite_recipes.values_list("id", flat=True))

			return JsonResponse({"recipes": construct_recipes(qs, self.inventory, table_id)})


		# search for an item, return just names for autocomplete
		if "search" in json_dict.keys():
			visible_recipes = self.get_recipe_queryset()
			all_items = Tinker.objects.filter(Q(ingredient__recipe__in=visible_recipes) | Q(prod__recipe__in=visible_recipes)).values_list("name", flat=True)

			return JsonResponse({"res": list(all_items.filter(name__iregex=json_dict["search"]).distinct())})


		# search for an item
		if "search_btn" in json_dict.keys():
			search = json_dict["search_btn"]
			recipe_qs = self.get_recipe_queryset()

			return JsonResponse({
				"as_product": construct_recipes(recipe_qs.filter(product__item__name__iregex=search), self.inventory),
				"as_ingredient": construct_recipes(recipe_qs.filter(ingredient__item__name__iregex=search), self.inventory),
			})


		# craft items out of others at a table
		if "craft" in json_dict.keys():

			try:
				id = int(json_dict["craft"])		# recipe id
				num = int(json_dict["num"])
			except:
				return JsonResponse({"message": "Parameter nicht lesbar angekommen"}, status=418)

			# get the product prototype
			recipe = get_object_or_404(self.get_recipe_queryset(set_perk_filter=False), id=id)

			# test if table owned
			if recipe.table and recipe.table.id not in self.inventory.keys():
				return JsonResponse({"message": "Tisch nicht vorhanden."}, status=418)
			
			# handle recipe that produces a perk:
			if recipe.produces_perk:
				num = 1
				if recipe.produces_known_perk:
					return JsonResponse({"message": "Den Perk hast du schon hergestellt."}, status=418)


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

			clean_inventory(self.relCrafting.profil)

			return JsonResponse({})


		# save new ordering of tables in profile model
		if "table_ordering" in json_dict.keys():

			self.relCrafting.profil.tableOrdering = [to for to in json_dict["table_ordering"] if to is not None]
			self.relCrafting.profil.save(update_fields=["tableOrdering"])

			return JsonResponse({})

		# toggle fav on recipe
		if "fav" in json_dict.keys():
			try:
				recipe_id = int(json_dict["fav"])
				recipe = get_object_or_404(Recipe, id=recipe_id)
			except:
				return JsonResponse({"message": "Parameter nicht lesbar angekommen"}, status=418)

			# add
			if not self.relCrafting.favorite_recipes.filter(id=recipe.id).exists():
				self.relCrafting.favorite_recipes.add(recipe)
			# remove
			else:
				self.relCrafting.favorite_recipes.remove(recipe)

			return JsonResponse({"num_favs": self.relCrafting.favorite_recipes.count()})


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


class SpGiveItemsView(VerifiedAccountMixin, SpielleitungOnlyMixin, ProfileSetMixin, TemplateView):
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
		return super().get_queryset().prefetch_related("permanently_needs").annotate(
			accessible = Exists(Profile.objects.filter(pk=self.relCrafting.profil.pk, region=OuterRef("pk"))),

			has_items = Count("permanently_needs", filter=Q(permanently_needs__inventoryitem__char=self.relCrafting.profil), distinct=True),
			needs_items = Count(F("permanently_needs"), distinct=True),
		)
	
	def get_context_data(self, **kwargs):
		drops = {region.pk: Tinker.objects.filter(drop__block__blockchance__region=region).distinct() for region in self.get_queryset()}

		return super().get_context_data(
			**kwargs,
            topic = "Regionen für {}".format(self.relCrafting.profil.name),
            app_index = "Crafting",
            app_index_url = reverse("crafting:craft"),

			drops = drops,
			profil = self.relCrafting.profil,
			combat_regions = CombatRegion.objects.prefetch_related("enemies").all(),
        )
	
	def post(self, *args, **kwargs):
		try:
			region = get_object_or_404(Region, id=int(self.request.POST.get("region_id")))
		except:
			messages.error(self.request, "Parameter nicht lesbar angekommen")
			return redirect("crafting:regions")



		if region.wooble_cost > self.relCrafting.profil.woobles:
			messages.error(self.request, "Das ist zu teuer für dich")
			return redirect("crafting:regions")


		self.relCrafting.profil.woobles -= region.wooble_cost
		self.relCrafting.profil.save(update_fields=["woobles"])

		region.allowed_profiles.add(self.relCrafting.profil)
		messages.success(self.request, f"Der weg in {region.__str__()} ist jetzt frei!")
		return redirect("crafting:regions")



class MiningView(VerifiedAccountMixin, ProfileSetMixin, DetailView):
	model = Region
	template_name = "crafting/mining.html"
	object = None

	def get_queryset(self):
		return super().get_queryset().annotate(
			accessible = Exists(Profile.objects.filter(pk=self.relCrafting.profil.pk, region=OuterRef("pk"))),

			has_items = Count("permanently_needs", filter=Q(permanently_needs__inventoryitem__char=self.relCrafting.profil), distinct=True),
			needs_items = Count(F("permanently_needs"), distinct=True),
		)

	def check_region_allowed(self):
		self.object = self.object or self.get_object()

		allowed = self.object.accessible and self.object.needs_items == self.object.has_items
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
			maxspeed = Coalesce(Subquery(tool_qs.filter(is_type=OuterRef("is_type")).values("speed")[:1]), 0),
		).filter(speed=F("maxspeed"))

		# inventory items
		items = InventoryItem.objects.prefetch_related("item").annotate(
			is_perk = Exists(MiningPerk.objects.filter(item=OuterRef("item"))),
		).filter(char=self.relCrafting.profil).order_by("item__name")

		# active perks
		perk_items = items.filter(is_perk=True).filter(Q(item__miningperk__region=None) | Q(item__miningperk__region=self.kwargs["pk"])).prefetch_related("item__miningperk")
		perks = list(MiningPerk.objects.filter(item__in=[i.item for i in perk_items]).values("item", "effect", "tool_type__name", "effect_increment", "stufe_wooble_price"))

		# num simultaneously displayed blocks
		block_count = 1
		block_perk_qs = MiningPerk.objects.filter(item__in=[i.item for i in perk_items], effect="block_count").annotate(
			stufe = Subquery(InventoryItem.objects.filter(char=self.relCrafting.profil, item=OuterRef("item")).values_list("num", flat=True)[:1])
		)
		for perk in block_perk_qs:
			for stufe in range(1, int(perk.stufe)+1):
				block_count += perk.effect_increment[str(stufe)]


		return super().get_context_data(
			**kwargs,
            topic = self.object.__str__(),
            app_index = "Region wechseln",
            app_index_url = reverse("crafting:regions"),

            profil = self.relCrafting.profil,
            items = items,
			block_pool = pool,
			blocks = blocks,
			block_count = block_count,
			tools = [tool.toDict() for tool in tools],
			perk_items = perk_items,
			perks = perks,
			tool_types = [*ToolType.objects.values_list("name", flat=True)],
        )
	
	def get(self, request, *args, **kwargs):
		redirectUrl = self.check_region_allowed()
		if redirectUrl: return redirect(redirectUrl)

		return super().get(request, *args, **kwargs)
    
	def post(self, *args, **kwargs):
		redirectUrl = self.check_region_allowed()
		if redirectUrl: return redirect(redirectUrl)

		json_dict = json.loads(self.request.body.decode("utf-8"))

		# gather all the details of one item to display them OR buy/sell items
		if "details" in json_dict.keys() or "item_id" in json_dict:
			return handle_overlay(json_dict, InventoryView(relCrafting=self.relCrafting).get_item_qs(), self.relCrafting.profil)

		if "drops" in json_dict and "time" in json_dict:
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
		
		if "perk_item" in json_dict:
			qs = InventoryItem.objects.annotate(
				cost = F("item__miningperk__stufe_wooble_price")
			)
			iitem = get_object_or_404(qs, char=self.relCrafting.profil, item=json_dict["perk_item"])
			
			
			cost = iitem.cost[str(int(iitem.num) + 1)]
			if cost > self.relCrafting.profil.woobles:
				return JsonResponse({"message": "Du kannst dir die nächste Stufe nicht leisten"}, status=418)
			
			self.relCrafting.profil.woobles -= cost
			self.relCrafting.profil.save(update_fields=["woobles"])

			iitem.num += 1
			iitem.save(update_fields=["num"])

			messages.success(self.request, f"Perk {iitem.item.name} auf Stufe {int(iitem.num)} verbessert")

			return JsonResponse({})
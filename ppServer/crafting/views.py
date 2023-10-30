import json
from random import randrange, random

from django.contrib.auth.decorators import login_required
from django.http.response import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404, reverse

from character.models import Spieler
from ppServer.decorators import spielleiter_only, verified_account
from shop.models import Tinker

from .forms import AddToInventoryForm
from .models import *
from .templatetags.duration import duration


@login_required
@verified_account
def index(request):

	if request.method == "GET":
		context = {
			"profiles": Profile.objects.all(),
			"topic": "Profilwahl",
			"app_index": "Crafting",
			"app_index_url": reverse("crafting:craft")
		}
		return render(request, "crafting/index.html", context)

	if request.method == "POST":
		name = request.POST.get("name")
		spieler = get_object_or_404(Spieler, name=request.user.username)

		# get or create profile with name
		profile, created = Profile.objects.get_or_create(name=name)
		if created:
			profile.owner = spieler
			profile.restricted = request.POST.get("restriction") is not None
			profile.save(update_fields=["owner", "restricted"])

		# set profile as current
		rel, _ = RelCrafting.objects.get_or_create(spieler=spieler)
		rel.profil = profile
		rel.save(update_fields=["profil"])

		return redirect("crafting:inventory")


@login_required
@verified_account
def inventory(request):

	spieler = get_object_or_404(Spieler, name=request.user.username)
	rel, _ = RelCrafting.objects.get_or_create(spieler=spieler)

	# no profile active? change that!
	if not rel.profil: return redirect("crafting:index")


	if request.method == "GET":

		context = {
			"topic": "Inventar von {}".format(rel.profil.name),
			"spielleiter": request.user.groups.filter(name__iexact="spielleiter").exists(),
			"add_form": AddToInventoryForm(),
			"restricted_profile": rel.profil.restricted,
			"duration": rel.profil.craftingTime,
			"items": InventoryItem.objects.filter(char=rel.profil).order_by("item__name").prefetch_related("item"),
			"app_index": "Crafting",
			"app_index_url": reverse("crafting:craft")
		}
		return render(request, "crafting/inventory.html", context)

	if request.method == "POST":

		json_dict = json.loads(request.body.decode("utf-8"))

		# add item to inventory without crafting
		if "item" in json_dict.keys():

			try:
				id = int(json_dict["item"])
				num = int(json_dict["num"])
			except:
				return JsonResponse({"message": "Konnte Parameter nicht lesbar empfangen"}, status=418)

			# add num of items and save
			item = get_object_or_404(Tinker, id=id)
			iitem, _ = InventoryItem.objects.get_or_create(char=rel.profil, item=item)
			iitem.num += num
			iitem.save(update_fields=["num"])

			return JsonResponse({})


		# gather all the details of one item to display them
		if "details" in json_dict.keys():

			try:
				iid = int(json_dict["details"])
			except:
				return JsonResponse({"message": "Konnte Parameter nicht lesbar empfangen"}, status=418)

			# get inventory item (has to exist, because clicked on it in inventory)
			iitem = get_object_or_404(InventoryItem, id=iid)
			prod = Product.objects.filter(item=iitem.item).first()

			weiteres = "illegal" if iitem.item.illegal else ""
			if iitem.item.lizenz_benötigt and not weiteres:
					weiteres = "Lizenz benötigt"
			if iitem.item.lizenz_benötigt and iitem.item.illegal:
					weiteres += ", Lizenz benötigt"

			data = {
					"id": iitem.item.id,
					"link": "{}#{}".format(reverse("shop:tinker"), iitem.item.id),
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


@login_required
@verified_account
def craft(request):

	spieler = get_object_or_404(Spieler, name=request.user.username)
	rel, _ = RelCrafting.objects.prefetch_related("profil").get_or_create(spieler=spieler)

	# no profile active? change that!
	if not rel.profil: return redirect("crafting:index")

	# collect current inventory
	inventory = {}
	for i in InventoryItem.objects.prefetch_related("item").filter(char=rel.profil):
			inventory[i.item.id] = i.num


	if request.method == "GET":

		# get all (used) table instances from db in alpabetical order
		table_list = rel.profil.getTables()
		for t in table_list: t["available"] = t["id"] in inventory.keys() or t["id"] == 0		# id == 0: special case for Handwerk (is always available)



		context = {
			"topic": table_list[0]["name"],
			"tables": table_list,
			"recipes": get_recipes_of_table(inventory, rel.profil.restricted, table_list[0]["id"] if len(table_list) else 0),
            "spielleiter": request.user.groups.filter(name__iexact="spielleiter").exists(),
		}
		return render(request, "crafting/craft.html", context)

	if request.method == "POST":

		json_dict = json.loads(request.body.decode("utf-8"))

		# table selection has changed, update the recipes
		if "table" in json_dict.keys():
			try:
				table_id = int(json_dict["table"])
			except: return JsonResponse({"message": "Parameter nicht lesbar angekommen"}, status=418)

			return JsonResponse({"recipes": get_recipes_of_table(inventory, rel.profil.restricted, table_id)})


		# search for an item, return just names for autocomplete
		if "search" in json_dict.keys():

			search = json_dict["search"]
			return JsonResponse({"res": [{"name": t.name} for t in Tinker.objects.filter(name__iregex=search) if not (rel.profil.restricted and not TinkerNeeds.objects.filter(product=t).exists())]})


		# search for an item
		if "search_btn" in json_dict.keys():
			search = json_dict["search_btn"]

			return JsonResponse({"as_product": construct_recipes(Product.objects.filter(item__name__iregex=search), inventory, rel),
                           "as_ingredient": construct_recipes(Ingredient.objects.filter(item__name__iregex=search), inventory, rel)})


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
			if recipe.table and recipe.table.id not in inventory.keys():
				return JsonResponse({"message": "Tisch nicht vorhanden."}, status=418)


			# test if enough ingredients exist and collect them in 'ingredients'. Keys are tinker_id's
			ingredients = {}
			for ni in recipe.ingredient_set.all():

				#  ingredient not owned. Abort.
				if not ni.item.id in inventory.keys(): return JsonResponse({"message": "Zu wenig Materialien vorhanden."}, status=418)

				num_owned = inventory[ni.item.id]
				debt = ni.num * num

				# insufficient amount of ingredients. Abort.
				if num_owned < debt: return JsonResponse({"message": "Zu wenig Materialien vorhanden."}, status=418)

				ingredients[ni.item.id] = debt		# save debt at inventoryItem id


			# subtract amounts
			for ni in InventoryItem.objects.filter(item__id__in=ingredients.keys(), char=rel.profil):

				# decrease ingredient amount
				if ni.num == ingredients[ni.item.id]:
					ni.delete()
				else:
					ni.num -= ingredients[ni.item.id]
					ni.save(update_fields=["num"])


			# add crafting time
			if rel.profil.craftingTime: rel.profil.craftingTime += recipe.duration * num
			else:						rel.profil.craftingTime  = recipe.duration * num

			rel.profil.save(update_fields=["craftingTime"])


			# save products
			for t in recipe.product_set.all():
				crafted, _ = InventoryItem.objects.get_or_create(char=rel.profil, item=t.item)
				crafted.num += t.num * num
				crafted.save(update_fields=["num"])

			return JsonResponse({})


		# save new ordering of tables in profile model
		if "table_ordering" in json_dict.keys():

			rel.profil.tableOrdering = [to for to in json_dict["table_ordering"] if to is not None]
			rel.profil.save(update_fields=["tableOrdering"])

			return JsonResponse({})


# queryset may contain either ingredients or products of recipes
def construct_recipes(queryset, inventory, rel):
	recipes = []
	recipe_ids = []
	for q in queryset:
		recipe = q.recipe

		# prevent duplicates
		if recipe.id in recipe_ids: continue
		recipe_ids.append(recipe.id)

		ingredients = recipe.ingredient_set.all()
		products = recipe.product_set.all()

		# restrict only to recipes that need ingredients, IF restricted
		if rel.profil.restricted and not ingredients.exists():
			continue

		recipe = {
			"id": recipe.id,
			"ingredients": [{"num": i.num, "own": inventory[i.item.id] if i.item.id in inventory.keys() else 0, "icon": i.item.getIconUrl(), "name": i.item.name} for i in ingredients],
			"products": [{"num": p.num, "icon": p.item.getIconUrl(), "name": p.item.name, "id": p.item.id} for p in products],
			"table": {"icon": recipe.table.getIconUrl(), "name": recipe.table.name} if recipe.table else Recipe.getHandwerk(),
			"locked": recipe.table.id not in inventory.keys() if recipe.table else False
		}
		recipes.append(recipe)

	return recipes


# inventory of a profile, restricted = profile.restricted, id = id of table
def get_recipes_of_table(inventory, restricted, id):

	# get all recipes that need the table with this id
	recipes = []
	for r in Recipe.objects.prefetch_related("ingredient_set__item", "product_set__item").filter(table__id=id if id else None):		# without table is represented by id=0, but need to query with table=None

		ingredients = r.ingredient_set.all()
		if restricted and not ingredients.exists(): continue

		products = r.product_set.all()

		recipe = {
			"id": r.id,
			"ingredients": [{"num": i.num, "own": inventory[i.item.id] if i.item.id in inventory.keys() else 0, "icon": i.item.getIconUrl(), "name": i.item.name} for i in ingredients],
			"products": [{"num": n.num, "icon": n.item.getIconUrl(), "name": n.item.name, "id": n.item.id} for n in products],
			"locked": id not in inventory.keys() if id else False		# special case again for Handwerk
		}
		recipes.append(recipe)

	return recipes


@login_required
@verified_account
def details(request, id):
	recipe = get_object_or_404(Recipe, id=id)
	context = {
		"topic": "Rezept",
		"ingredients": [{"link": "{}#{}".format(reverse("shop:tinker"), e.item.id), "name": e.item.name, "num": e.num, "icon": e.item.getIconUrl()} for e in recipe.ingredient_set.all()],
		"products": [{"link": "{}#{}".format(reverse("shop:tinker"), e.item.id), "name": e.item.name, "num": e.num, "icon": e.item.getIconUrl()} for e in recipe.product_set.all()],
		"table": {
			"link": "{}#{}".format(reverse("shop:tinker"), recipe.table.id),
			"name": recipe.table.name,
			"icon": recipe.table.getIconUrl()
			} if recipe.table else Recipe.getHandwerk(),
		"spezial": ", ".join([e.titel for e in recipe.spezial.all()]),
		"wissen": ", ".join([e.titel for e in recipe.wissen.all()]),
		"duration": recipe.duration,
		"app_index": "Crafting",
		"app_index_url": reverse("crafting:craft")
	}
	return render(request, "crafting/details.html", context)


@login_required
@spielleiter_only(redirect_to="crafting:craft")
def sp_give_items(request):

	if request.method == "GET":
		context = {
			"topic": "Profilen Items geben",
			"allProfiles": sorted([{"name": p.name, "id": p.id, "restricted": p.restricted} for p in Profile.objects.all()], key=lambda p: p["name"]),
			"allItems": sorted([{"icon": t.getIconUrl(), "id": t.id, "name": t.name} for t in Tinker.objects.all()], key=lambda t: t["name"]),
			"app_index": "Crafting",
			"app_index_url": reverse("crafting:craft")
		}
		return render(request, "crafting/sp_give_items.html", context)

	if request.method == "POST":
		json_dict = json.loads(request.body.decode("utf-8"))

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




def get_2nd_chance_material(prev_material, materials):
	chance = randrange(1, 101)
	return prev_material if chance <= prev_material.second_spawn_chance else get_rand_material(materials)

def get_rand_material(materials):
	sum_chances = sum([material.spawn_chance for material in materials])
	chance = random() * sum_chances
	
	for material in materials:
		chance -= material.spawn_chance

		if chance <= 0:
			return  material

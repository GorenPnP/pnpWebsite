import random

from django.shortcuts import render, get_object_or_404, reverse, redirect
from django.contrib.auth.decorators import login_required
from django.http.response import JsonResponse
from django.db.utils import IntegrityError
from django.forms.models import model_to_dict

from ppServer.decorators import spielleiter_only

from .models import *


@login_required
@spielleiter_only(redirect_to="base:index")
def region_select(request):
	context = {
		"topic": "Region",
		"regions": [{"id": r.id, "name": r.name} for r in Region.objects.all()],
		"plus_url": reverse("mining:create_region")}
	return render(request, "mining/region_select.html", context)


@login_required
@spielleiter_only(redirect_to="mining:region_select")
def region_editor(request, region_id=None):

	# make sure region exists
	if region_id is None:
		region = Region.objects.create()
		return redirect(reverse("mining:region_editor", args=[region.id]))

	region = get_object_or_404(Region, id=region_id)


	if request.method == "GET":

		groups = [g for g in MaterialGroup.objects.all()]
		grouped_material_ids = []
		for group in groups:
			grouped_material_ids += [m.id for m in group.materials.all()]
		
		ungrouped_materials = Material.objects.exclude(id__in=grouped_material_ids)

		# serializeable layers & their entities & their materials :)
		layers = [layer.toDict() for layer in Layer.objects.filter(region=region)]
		materials = [material.toDict() for material in Material.objects.all()]


		# get max x & y coords of all entities of all layers
		width = max([ max([entity["x"] + entity["w"] for entity in layer["entities"]])  for layer in layers if len(layer["entities"])] + [0])
		height = max([ max([entity["y"] + entity["h"] for entity in layer["entities"]])  for layer in layers if len(layer["entities"])] + [0])

		context = {
			"topic": region.name if region.name else "New Region",
			"groups": groups + [{"name": "-", "materials": ungrouped_materials}],
			"materials": materials,
			"layers": layers,
			"field_width": width,
			"field_height": height,
			"name": region.name,
			"bg_color": region.bg_color_rgb,
			"char_index": region.layer_index_of_char
		}
		return render(request, "mining/region_editor.html", context)


	if request.method == "POST":
		json_dict = json.loads(request.body.decode("utf-8"))
		name = json_dict["name"]
		entities = json.loads(json_dict["fields"])
		bg_color = json_dict["bg_color"]

		if (not name or not entities):
			return JsonResponse({"message": "Parameters name and fields are required"}, status=418)
			

		region.name = name
		region.bg_color_rgb = bg_color
		try:
			region.save()
		except IntegrityError as e:
			print(e)
			return JsonResponse({"message": "Den Namen '{}' gibt es schon".format(name)}, status=418)


		for layer in Layer.objects.filter(region=region):
			layer.entity_set.all().delete()

		for entity in entities:
			layer_id = int(entity["layer"])
			layer = Layer.objects.get(id=layer_id, region=region)

			if region.layer_index_of_char != layer.index:
				material_id = int(entity["material"]["id"])
				material = Material.objects.get(id=material_id)
			else: material = Material.objects.first()

			Entity.objects.create(layer=layer, x=entity["x"], y=entity["y"],
				material=material, mirrored=entity["mirrored"], scale=entity["scale"], rotation_angle=entity["rotation_angle"])

		return JsonResponse({"message": "ok"})


@login_required
@spielleiter_only(redirect_to="mining:region_select")
def mining(request, pk):
	region = get_object_or_404(Region, pk=pk)

	if request.method == "GET":
		
		# if no materials defined for this region, redirect away
		if not region.layer_set.count(): return redirect("mining:region_select")

		layers = [model_to_dict(layer) for layer in region.layer_set.exclude(index=region.layer_index_of_char)]
		char_field = get_object_or_404(Layer, region=region, index=region.layer_index_of_char).field

		# make materials json-serializable
		materials = [model_to_dict(material) for material in Material.objects.all()]
		for material in materials:
			material["icon"] = material["icon"].url

		# get possible spawn points
		char_spawns = []
		for y in range(len(char_field)):
			for x in range(len(char_field[y])):
				if char_field[y][x] is not None:
					char_spawns.append({"x": x, "y": y})

		# no spawn location set :(
		if not len(char_spawns): return redirect("mining:region_select")


		context = {
			"topic": region.name,
			"layers": layers,
			"field_width": len(layers[0]["field"][0]),
			"field_height": len(layers[0]["field"]),
			"materials": materials,
			"bg_color": region.bg_color_rgb,
			"spawn_point": random.choice(char_spawns),
			"char_layer_index": region.layer_index_of_char
		}
		return render(request, "mining/mining.html", context)
	
	if request.method == "POST":
		prev_material_id = json.loads(request.body.decode("utf-8"))['id']
		prev_material = get_object_or_404(Material, id=prev_material_id)

		spieler = get_object_or_404(Spieler, name=request.user.username)
		rel = get_object_or_404(RelCrafting, spieler=spieler)

		log_drops = []
		for drop in MaterialDrop.objects.filter(material=prev_material):
			item = drop.item
			amount = choice(json.loads(drop.amount))

			# add to inventory
			iitem, _ = InventoryItem.objects.get_or_create(char=rel.profil, item=item)
			iitem.num += amount
			iitem.save()

			# log drops
			log_drops.append([amount, item.name])


		return JsonResponse({
			"id": get_2nd_chance_material(prev_material, Material.objects.filter(region=region)).id,
			"amount": json.dumps(log_drops)
		})


def shooter(request):
	return render(request, "mining/shooter.html", {})


@login_required
@spielleiter_only(redirect_to="mining:region_select")
def game(request, pk):
	region = get_object_or_404(Region, pk=pk)

	if request.method == "GET":
		
		# if no materials defined for this region, redirect away
		if not region.layer_set.count(): return redirect("mining:region_select")
		
		# serializeable layers & their entities & their materials :)
		layers = [layer.toDict() for layer in Layer.objects.filter(region=region)]


		# get max x & y coords of all entities of layers
		width = max([ max([entity["x"] + entity["w"] for entity in layer["entities"]])  for layer in layers if len(layer["entities"])] + [0])
		height = max([ max([entity["y"] + entity["h"] for entity in layer["entities"]])  for layer in layers if len(layer["entities"])] + [0])

		context = {
			"topic": region.name if region.name else "New Region",
			"layers": layers,
			"field_width": width,
			"field_height": height,
			"name": region.name,
			"region_id": region.id,
			"bg_color": region.bg_color_rgb,
			"char_index": region.layer_index_of_char
		}
	return render(request, "mining/game.html", context)
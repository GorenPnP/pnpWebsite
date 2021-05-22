import random

from django.shortcuts import render, get_object_or_404, reverse, redirect
from django.contrib.auth.decorators import login_required
from django.http.response import JsonResponse
from django.db.utils import IntegrityError
from django.forms.models import model_to_dict

from ppServer.decorators import spielleiter_only
from crafting.models import RelCrafting

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

		groups = [g.toDict() for g in MaterialGroup.objects.all()]
		grouped_material_ids = []
		for group in groups:
			grouped_material_ids += [m["id"] for m in group["materials"]]
		
		ungrouped_materials = [m.toDict() for m in Material.objects.exclude(id__in=grouped_material_ids)]

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
			"char_index": region.layer_index_of_char,
			"profile": "Profil " + RelCrafting.objects.get(spieler__name=request.user.username).profil.name
		}
	return render(request, "mining/game.html", context)
	
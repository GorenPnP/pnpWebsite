import json

from django.shortcuts import render, get_object_or_404, reverse, redirect
from django.contrib.auth.decorators import login_required
from django.http.response import JsonResponse
from django.db.utils import IntegrityError

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



def get_modified_fields(fields):
	criteria = [
		{"path": ["material", "id"], "value": lambda f: int(f["material"]["id"])},
		{"path": ["layer", "id"], "value": lambda f: int(f["layer"])},
		{"path": ["x"], "value": lambda f: f["x"]},
		{"path": ["y"], "value": lambda f: f["y"]},
		{"path": ["mirrored"], "value": lambda f: f["mirrored"]},
		{"path": ["scale"], "value": lambda f: f["scale"]},
		{"path": ["rotation_angle"], "value": lambda f: f["rotation_angle"]},
	]

	modified_fields = []
	for field in [field for field in fields if "id" in field.keys()]:
		entity = Entity.objects.get(id=field["id"])

		# go though all criteria
		for criterium in criteria:
			obj = entity
			equal = True
			for part in criterium["path"]: obj = getattr(obj, part)

			if obj != criterium["value"](field):
				equal = False
				break
		
		# if >= 1 difference found, add the entity(old)-field(new) pair to return them
		if not equal: modified_fields.append({"field": field, "entity": entity})
	return modified_fields


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

		# all remaining entities (all that have ids) 
		remaining_entity_ids = [int(entity["id"]) for entity in entities if "id" in entity.keys()]


		# delete all persistent ones which are not in remaining entities
		for layer in Layer.objects.filter(region=region):
			layer.entity_set.exclude(id__in=remaining_entity_ids).delete()


		# all modified entities
		for mod in get_modified_fields(entities):
			field = mod["field"]
			entity = mod["entity"]

			entity.layer =  Layer.objects.get(id=field["layer"])
			entity.x = field["x"]
			entity.y = field["y"]
			entity.material = Material.objects.get(id=field["material"]["id"])
			entity.mirrored = field["mirrored"]
			entity.scale = field["scale"]
			entity.rotation_angle = field["rotation_angle"]
			entity.save()



		# all new entities
		for entity in [e for e in entities if "id" not in e.keys()]:

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
# @spielleiter_only(redirect_to="mining:region_select")
def game(request, pk):
	region = get_object_or_404(Region, pk=pk)

	if request.method == "GET":

		spieler = Spieler.objects.get(name=request.user.username)
		profile = RelCrafting.objects.get(spieler=spieler).profil
		ProfileEntity.update(region, profile)

		# no spawn point, redirect
		if not ProfileEntity.objects.filter(profil=profile, entity__layer__index=region.layer_index_of_char).count():
			return redirect("mining:region_select")

		# serializeable layers & their entities & their materials :)
		existing_entity_ids = [pe.entity.id for pe in ProfileEntity.objects.exclude(entity=None).filter(profil=profile, entity__layer__region=region)]
		layers = [layer.toDict() for layer in Layer.objects.filter(region=region)]

		# remove already mined entities
		for layer in layers:
			layer["entities"] = [e for e in layer["entities"] if e["id"] in existing_entity_ids]

		# collect inventory
		rel_profile, _ = RelProfile.objects.get_or_create(spieler=spieler, profile=profile)
		if not rel_profile.inventory:
			rel_profile.inventory = Inventory.objects.create()
			rel_profile.save()

		inventory = rel_profile.inventory
		inventory_items = [iitem.toDict() for iitem in InventoryItem.objects.filter(inventory=inventory)]

		context = {
			"topic": region.name if region.name else "New Region",
			"layers": layers,
			"name": region.name,
			"region_id": region.id,
			"bg_color": region.bg_color_rgb,
			"char_index": region.layer_index_of_char,
			"profile": "Profil " + profile.name,
			"username": request.user.username,
			"inventory": {"width": inventory.width, "height": inventory.height},
			"inventory_items": inventory_items,
		}
	return render(request, "mining/game.html", context)
	
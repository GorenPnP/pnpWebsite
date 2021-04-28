from django.shortcuts import render, get_object_or_404, reverse
from django.contrib.auth.decorators import login_required
from django.http.response import JsonResponse
from django.db.utils import IntegrityError

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
	region = get_object_or_404(Region, id=region_id) if region_id is not None else None

	if request.method == "GET":

		groups = [g for g in MaterialGroup.objects.all()]
		grouped_material_ids = []
		for group in groups:
			grouped_material_ids += [m.id for m in group.materials.all()]
		
		ungrouped_materials = Material.objects.exclude(id__in=grouped_material_ids)

		layers = Layer.objects.filter(region=region) if region else []
		width = max([  max([len(row) for row in layer.field])  for layer in layers]) if region else 0
		height = max([len(layer.field) for layer in layers]) if region else 0
		context = {
			"topic": region.name if region else "New Region",
			"groups": groups + [{"name": "-", "materials": ungrouped_materials}],
			"materials": Material.objects.all(),
			"layers": layers,
			"field_width": width,
			"field_height": height,
			"name": region.name if region else ""
		}
		return render(request, "mining/region_editor.html", context)

	if request.method == "POST":
		json_dict = json.loads(request.body.decode("utf-8"))
		name = json_dict["name"]
		fields = json.loads(json_dict["fields"])

		if (not name or not fields):
			return JsonResponse({"message": "Parameters name and material_grid are required"}, status=418)

		if region is None: 
			try:
				region = Region.objects.create(name=name)
			except IntegrityError as e:
				print(e)
				return JsonResponse({"message": "Den Namen '{}' gibt es schon".format(name)}, status=418)

		region.name = name
		region.save()

		for layer_id, field in fields.items():
			layer_id = int(layer_id) if layer_id else None
			layer = Layer.objects.get(id=layer_id, region=region) if layer_id and layer_id > 0 else None
			if not layer:
				layer = Layer.objects.create(region=region, field=field)

			layer.field = field
			layer.save()

		return JsonResponse({"message": "ok"})


@login_required
@spielleiter_only(redirect_to="mining:region_select")
def mining(request, pk):
	region = get_object_or_404(Region, pk=pk)

	if request.method == "GET":
		
		# if no materials defined for this region, redirect away
		if not region.layer_set.count(): return redirect("mining:region_select")

		print(region.layer_set.all())

		context = {
			"topic": region.name,
			"layers": region.layer_set.all(),
			"materials": Material.objects.all()
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
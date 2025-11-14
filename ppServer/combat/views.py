import json

from django.contrib import messages
from django.shortcuts import render, reverse, redirect
from django.views.generic import DetailView
from django.views.generic.list import ListView

from crafting.mixins import ProfileSetMixin
from crafting.models import InventoryItem
from ppServer.mixins import VerifiedAccountMixin, SpielleitungOnlyMixin

from .forms import *
from .models import *


class RegionSelectView(VerifiedAccountMixin, SpielleitungOnlyMixin, ListView):
	template_name = "combat/region_select.html"
	model = Region
	redirect_to = "crafting:regions"

	def get_context_data(self, **kwargs):
		relCrafting = getattr(self, "relCrafting", None)

		return super().get_context_data(
			**kwargs,
			topic = "Kämpfen für " + (relCrafting.profil.name if relCrafting else "-"),
			app_index = "Crafting",
			app_index_url = reverse("crafting:craft"),
		)

	def post(self, *args, **kwargs):
		name = self.request.POST.get("name")
		region = Region.objects.create(name=name)
		return redirect(reverse("combat:region_editor", args=[region.pk]))


class RegionEditorView(VerifiedAccountMixin, SpielleitungOnlyMixin, DetailView):
	template_name = "combat/region_editor.html"
	model = Region

	def get_context_data(self, **kwargs):
		return super().get_context_data(
			**kwargs,
			topic = self.object.name,
			app_index = "Region wählen",
			app_index_url = reverse("combat:region_select"),

			grid_size = Region.GRID_SIZE,
			types = list(CellType.objects.annotate_sprite(self.object).values("pk", "name", "sprite", "use_default_sprite")),
			empty_type_pk = CellType.objects.filter(is_default_sprite=True).values_list("pk", flat=True).first(),
			form = RegionEditorForm(instance=self.object),
			enemy_formset = get_EnemyFormset(self.object)(initial=RegionEnemy.objects.filter(region=self.object).values("enemy", "num"), queryset=self.model.objects.none()),
			enemy_formset_helper = EnemyFormsetHelper(),
		)
	
	def post(self, *args, **kwargs):
		self.object = self.get_object()

		form = RegionEditorForm(self.request.POST, self.request.FILES, instance=self.object)
		enemy_formset = get_EnemyFormset(self.object)(self.request.POST, self.request.FILES, queryset=self.model.objects.none())
		form.full_clean()

		if form.is_valid() and enemy_formset.is_valid():

			# save (grid of) region
			self.object = form.save()

			# save enemies (with region)
			for regionenemy in enemy_formset.save(commit=False):
				regionenemy.region = self.object
				regionenemy.save()

			# save regional sprites
			for cell_type in CellType.objects.all():
				sprite = self.request.FILES.get(f"type-{cell_type.pk}", None)
				if sprite:
					RegionalSprite.objects.update_or_create(region=self.object, type=cell_type, defaults={"sprite": sprite})

			# redirect
			messages.success(self.request, "Speichern war erfolgreich")
			return redirect(self.request.build_absolute_uri())
		else:
			messages.error(self.request, "Fehler beim Speichern")
			context = self.get_context_data()
			context["form"] = form
			return render(self.request, self.template_name, context)
	

class FightView(VerifiedAccountMixin, ProfileSetMixin, DetailView):
	template_name = "combat/fight.html"
	model = Region

	def get_context_data(self, **kwargs):
		default_sprite = CellType.objects.annotate_sprite(self.object).filter(is_default_sprite=True).values_list("sprite", flat=True).first()
		player_stats, _ = PlayerStats.objects.get_or_create(profil=self.relCrafting.profil, char=self.relCrafting.char)

		return super().get_context_data(
			**kwargs,
			topic = self.object.name + " für " + self.relCrafting.profil.name,
			app_index = "Region wählen",
			app_index_url = reverse("combat:region_select"),

			grid_size = Region.GRID_SIZE,
			types = {
				type["pk"]: {
					**type,
					"sprite": default_sprite if type["use_default_sprite"] else type["sprite"],
				}
				for type in CellType.objects.annotate_sprite(self.object).values("pk", "sprite", "use_default_sprite", "spawn", "enemy_spawn", "obstacle", "exit")
			},
			player_stats = player_stats.toDict(),
			enemies = [{"num": e.num, "enemy": e.enemy.toDict()} for e in self.object.regionenemy_set.all()]
		)
	
	def post(self, *args, **kwargs):
		loot = json.loads(self.request.POST.get("loot"))
		profil = self.relCrafting.profil

		for item in Tinker.objects.filter(pk__in=loot.keys()):
			iitem, _ = InventoryItem.objects.get_or_create(char=profil, item=item, defaults={"num": 0})
			iitem.num += loot[str(item.pk)]
			iitem.save(update_fields=["num"])

		return redirect("combat:region_select")

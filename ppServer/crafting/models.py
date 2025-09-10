from datetime import timedelta

from django.db import models, transaction
from django.db.models import Subquery, OuterRef, F, Case, When
from django.core.validators import MinValueValidator, MaxValueValidator

from django_resized import ResizedImageField

from character.models import Spieler, Spezialfertigkeit, Wissensfertigkeit, Charakter
from shop.models import Tinker


############### Profiles & Inventory #################

class RunningRealtimeRecipe(models.Model):
	class Meta:
		ordering = ["profil", "finishes_at", "recipe", "num"]

	recipe = models.ForeignKey("Recipe", on_delete=models.CASCADE)
	profil = models.ForeignKey("Profile", on_delete=models.CASCADE)

	num = models.PositiveIntegerField(validators=[MinValueValidator(1)])
	starts_at = models.DateTimeField(auto_now_add=True)
	begins_at = models.DateTimeField()
	finishes_at = models.DateTimeField()

	def distribute_products_and_stop(self):
		with transaction.atomic():

			# update existing iitems
			InventoryItem.objects\
				.filter(char=self.profil, item__in=self.recipe.product_set.values_list("item_id", flat=True))\
				.annotate(add = Subquery(Product.objects.filter(recipe=self.recipe, item=OuterRef("item")).values_list("num", flat=True)))\
				.update(num=F("num") + (F("add") * self.num))
			
			# create new iitems
			new_iitems = [InventoryItem(item=product.item, num=product.num*self.num, char=self.profil) for product in self.recipe.product_set.exclude(item__in=InventoryItem.objects.filter(char=self.profil).values_list("item_id", flat=True))]
			if new_iitems: InventoryItem.objects.bulk_create(new_iitems)

			# end realtime execution of recipe
			self.delete()

class RelCrafting(models.Model):
	class Meta:
		ordering = ["spieler"]

		verbose_name = "Crafting von Spieler"
		verbose_name_plural = "Crafting von Spielern"

	spieler = models.OneToOneField(Spieler, on_delete=models.CASCADE)
	profil = models.ForeignKey("Profile", on_delete=models.SET_NULL, null=True, blank=True)

	char = models.ForeignKey(Charakter, on_delete=models.SET_NULL, null=True, blank=True)
	favorite_recipes = models.ManyToManyField("Recipe")

	def __str__(self):
		return "{} aktiv mit {}".format(self.spieler.name if self.spieler else "-", self.profil.name if self.profil else "-")


class Profile(models.Model):
	class Meta:
		ordering = ["name"]
		verbose_name = "Profil"
		verbose_name_plural = "Profile"

	owner = models.ForeignKey(Spieler, on_delete=models.SET_NULL, null=True)
	name = models.CharField(max_length=100, unique=True)

	miningTime = models.DurationField('mining time (hh:mm:ss)', null=True, blank=True, default=timedelta(minutes=0))
	craftingTime = models.DurationField('crafting time (hh:mm:ss)', null=True, blank=True, default=timedelta(minutes=0))
	tableOrdering = models.JSONField(default=list)

	electricity = models.FloatField(default=0.0)
	thermic = models.FloatField(default=0.0)
	woobles = models.FloatField(default=0.0, validators=[MinValueValidator(0.0)])

	restricted = models.BooleanField(default=False)

	def __str__(self):
		return self.name


	def getTables(self, iitem_ids: list[int], tinker_id=None) -> list[dict["id", "name", "icon"]]:

		# get tables
		rawTables = Table.objects.prefetch_related("item", "part")\
			.annotate(
				used = Subquery(ProfileTableDurability.objects.filter(char=self, table=OuterRef("pk")).values_list("recipes_crafted", flat=True)),
				durability_left = F("durability") - F("used"),
				percent_durability_left = Case(When(durability=0, then=0), default=100 * (F("durability") - F("used")) / F("durability") +0.5, output_field=models.IntegerField())
			)\
			.order_by("item__name")
		if tinker_id is not None: rawTables = rawTables.filter(item__id=tinker_id)

		tables = [Recipe.getHandwerk()]
		for t in rawTables:
			tables.append({
				"id": t.item.id, "name": t.item.name, "icon": t.item.getIconUrl(),
				"percent_durability_left": t.percent_durability_left,
				"durability_left": t.durability_left,
				"part": t.part.toDict() if t.part else None,
				"owns_part": t.part.id in iitem_ids if t.part else False,
			})

		if tinker_id is not None: return tables[-1]

		# get & use order
		order = self.tableOrdering
		ordered_tables = []

		# default alphabetical ordering but beginning with Handwerk
		if not order: return tables

		# sort by ids of ordering
		for o in order:
			table = next((t for t in tables if t["id"] == o), None)

			# skip over in case a table is removed after saving ordering to db
			if table is None: continue

			# append tables in order
			ordered_tables.append(table)

		# return custom ordered + rest
		return ordered_tables + [t for t in tables if t not in ordered_tables]


class InventoryItem(models.Model):

	class Meta:
		ordering = ["char", "item"]
		unique_together = ("char", "item")

		verbose_name = "Inventar Item"
		verbose_name_plural = "Inventar Items"

	char = models.ForeignKey(Profile, on_delete=models.CASCADE)
	item = models.ForeignKey(Tinker, on_delete=models.CASCADE)

	num = models.FloatField(default=0, validators=[MinValueValidator(0)])

	def __str__(self):
		return "{}x {} von {}".format(self.num, self.item.name, self.char.name)



############### Recipes #################

class Ingredient(models.Model):

	class Meta:
		verbose_name = "Zutat"
		verbose_name_plural = "Zutaten"

	num = models.FloatField(default=1.0, validators=[MinValueValidator(0)])

	item = models.ForeignKey(Tinker, on_delete=models.CASCADE, related_name="ingredient", related_query_name="ingredient")
	recipe = models.ForeignKey("Recipe", on_delete=models.CASCADE)

	def __str__(self):
		return "Rezept {} benötigt {}x {}".format(self.recipe.id, self.num, self.item)


class Product(models.Model):

	class Meta:
		verbose_name = "Produkt"
		verbose_name_plural = "Produkte"

	num = models.FloatField(default=1.0, validators=[MinValueValidator(0)])

	item = models.ForeignKey(Tinker, on_delete=models.CASCADE, related_name="prod", related_query_name="prod")
	recipe = models.ForeignKey("Recipe", on_delete=models.CASCADE)

	def __str__(self):
		return "Rezept {} produziert {}x {}".format(self.recipe.id, self.num, self.item)

class Table(models.Model):
	class Meta:
		verbose_name = "Werkstätte"
		verbose_name_plural = "Werkstätten"

		ordering = ("item", "part")

	durability = models.PositiveSmallIntegerField(default=0, help_text="in #Rezepte")
	part = models.ForeignKey(Tinker, on_delete=models.SET_NULL, null=True, blank=True, related_name="part")

	item = models.ForeignKey(Tinker, on_delete=models.CASCADE)

	def __str__(self):
		return "Werkstätte {}".format(self.item)

class ProfileTableDurability(models.Model):
	class Meta:
		ordering = ["char", "table"]
		unique_together = ("char", "table")

	table = models.ForeignKey(Table, on_delete=models.CASCADE)
	char = models.ForeignKey(Profile, on_delete=models.CASCADE)

	recipes_crafted = models.PositiveIntegerField(default=0)	# max:table.duration. At that point broken until new part added and set to 0


class Recipe(models.Model):

	class Meta:
		verbose_name = "Rezept"
		verbose_name_plural = "Rezepte"

	table = models.ForeignKey(Table, on_delete=models.CASCADE, null=True, blank=True)
	duration = models.DurationField('herstellungsdauer (hh:mm:ss)', default=timedelta(seconds=0), null=True, blank=True)

	spezial = models.ManyToManyField(Spezialfertigkeit, blank=True)
	wissen = models.ManyToManyField(Wissensfertigkeit, blank=True)

	def __str__(self):
		return "Rezept für {} an {}".format([p for p in self.product_set.all()], self.table)

	# to display a table in /crafting for all recipes without an actual table
	@staticmethod
	def getHandwerk():
		return {"name": "Handwerk", "icon": "/static/crafting/img/Handwerk.png", "id": 0, "available": True, "link": None}


############### Mining #################

class ToolType(models.Model):

	class Meta:
		verbose_name = "Tool Type"
		verbose_name_plural = "Tool Types"
		ordering = ["name"]

	name = models.CharField(max_length=64, unique=True)

	def __str__(self):
		return f"ToolType {self.name}"

class Region(models.Model):

	class Meta:
		verbose_name = "Region"
		verbose_name_plural = "Regionen"

		ordering = ["wooble_cost", "name"]

	icon = ResizedImageField(size=[64, 64])
	name = models.CharField(max_length=64, unique=True)
	wooble_cost = models.FloatField(default=0.0, validators=[MinValueValidator(0.0)])
	permanently_needs = models.ManyToManyField(Tinker, blank=True)

	allowed_profiles = models.ManyToManyField(Profile, blank=True)

	def __str__(self):
		return "Region {}".format(self.name)



class BlockChance(models.Model):
	class Meta:
		verbose_name = "Block Chance"
		verbose_name_plural = "Block Chances"
		ordering = ["-chance"]

	region = models.ForeignKey(Region, on_delete=models.CASCADE)
	block = models.ForeignKey("Block", on_delete=models.CASCADE)

	chance = models.PositiveSmallIntegerField(default=1, validators=[MinValueValidator(1)], help_text="Higher is appears more often. # copies goes into a pool to randomly select the next block.")

class Drop(models.Model):
	class Meta:
		verbose_name = "Block Drop"
		verbose_name_plural = "Block Drops"
		ordering = ["-chance"]
	
	item = models.ForeignKey(Tinker, on_delete=models.CASCADE)
	block = models.ForeignKey("Block", on_delete=models.CASCADE)

	chance = models.FloatField(default=50, validators=[MinValueValidator(0.0), MaxValueValidator(100.0)], help_text="Probabiliy of (0%, 100%]")

	def toDict(self):
		return {
			"chance": self.chance,
			"item": self.item.toDict(),
		}

class Block(models.Model):

	class Meta:
		verbose_name = "Block"
		verbose_name_plural = "Blöcke"

	icon = ResizedImageField(size=[64, 64])
	name = models.CharField(max_length=64, unique=True)

	hardness = models.PositiveIntegerField(default=1)
	effective_tool = models.ManyToManyField(ToolType, blank=True)

	chance = models.ManyToManyField(Region, through=BlockChance)
	drops = models.ManyToManyField(Tinker, through=Drop)

	def __str__(self):
		return "Block {}".format(self.name)
	
	def toDict(self):
		fields = [
			"name",
			"hardness",
		]
		return {
			"icon": self.icon.url if self.icon else None,
			"drops": [d.toDict() for d in self.drop_set.all()],
			"effective_tool": ", ".join(self.effective_tool.values_list("name", flat=True)),
			**{field: getattr(self, field) for field in fields}
		}


class Tool(models.Model):

	class Meta:
		verbose_name = "Werkzeug"
		verbose_name_plural = "Werkzeuge"
		ordering = ["-speed", "is_type__name", "item"]

	item = models.OneToOneField(Tinker, on_delete=models.CASCADE)
	speed = models.PositiveIntegerField(default=1)
	is_type = models.ManyToManyField(ToolType, blank=False)

	def __str__(self):
		return "Werkzeug {} ({})".format(self.item.name, self.speed)
	
	def toDict(self):
		return {
			"item": self.item.toDict(),
			"speed": self.speed,
			"is_type": ", ".join(self.is_type.values_list("name", flat=True))
		}


class MiningPerk(models.Model):

	class Meta:
		verbose_name = "Mining-Perk"
		verbose_name_plural = "Mining-Perks"
		ordering = ["region", "effect", "item__name", "tool_type__name"]

	Effect = models.TextChoices("Effect", "speed multidrop block_count spread")
	def default_perk_dict(): return {i: 1.0 for i in range(1, 11)}

	beschreibung = models.TextField()

	# what does it do?
	effect = models.CharField(max_length=32, choices=Effect.choices, default="speed")
	tool_type = models.ManyToManyField(ToolType, blank=True)
	effect_increment = models.JSONField(default=default_perk_dict, null=False, blank=False)

	# when does it apply?
	item = models.OneToOneField(Tinker, on_delete=models.CASCADE, null=True)
	region = models.ForeignKey(Region, on_delete=models.CASCADE, null=True, blank=True)
	stufe_wooble_price = models.JSONField(default=default_perk_dict, null=False, blank=False)

	def __str__(self):
		return self.get_effect_display() + " " + (", ".join(self.tool_type.values_list("name", flat=True)) or "global")
import json
from datetime import timedelta

from django.db import models
from django.core.validators import MinValueValidator

from character.models import Spieler, Spezialfertigkeit, Wissensfertigkeit
from shop.models import Tinker


class RelCrafting(models.Model):
	class Meta:
		ordering = ["spieler"]

		verbose_name = "Crafting von Spieler"
		verbose_name_plural = "Crafting von Spielern"

	spieler = models.OneToOneField(Spieler, on_delete=models.CASCADE)
	profil = models.ForeignKey("Profile", on_delete=models.SET_NULL, null=True, blank=True)

	def __str__(self):
		return "{} aktiv mit {}".format(self.spieler.name, self.profil.name)


class Profile(models.Model):
	class Meta:
		ordering = ["name"]
		verbose_name = "Profil"
		verbose_name_plural = "Profile"

	owner = models.ForeignKey(Spieler, on_delete=models.SET_NULL, null=True)
	name = models.CharField(max_length=100, unique=True)

	craftingTime = models.DurationField(null=True, blank=True, default=timedelta(minutes=0))
	tableOrdering = models.TextField(default="[]")

	electricity = models.FloatField(default=0.0)
	thermic = models.FloatField(default=0.0)

	restricted = models.BooleanField(default=False)

	def __str__(self):
		return self.name


	def getTables(self):

		# get tables
		rawTables = Recipe.getTables()
		tables = [{ "id": t.id, "name": t.name, "icon": t.getIconUrl() } for t in rawTables]

		# get & use order
		order = json.loads(self.tableOrdering)
		ordered_tables = []

		# default alphabetical ordering but beginning with Handwerk
		if not order:
			return [Recipe.getHandwerk()] + tables

		# sort by ids of ordering
		for o in order:
			if o == 0:
				ordered_tables.append(Recipe.getHandwerk())
				continue

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


class Recipe(models.Model):

	class Meta:
		verbose_name = "Rezept"
		verbose_name_plural = "Rezepte"

	table = models.ForeignKey(to=Tinker, on_delete=models.CASCADE, null=True, blank=True)
	duration = models.DurationField('herstellungsdauer (dd:hh:mm)', default=timedelta(minutes=0), null=True, blank=True)

	spezial = models.ManyToManyField(Spezialfertigkeit, blank=True)
	wissen = models.ManyToManyField(Wissensfertigkeit, blank=True)

	def __str__(self):
		return "Rezept für {} an {}".format([p for p in self.product_set.all()], self.table)

	# to display a table in /crafting for all recipes without an actual table
	@staticmethod
	def getHandwerk():
		return {"name": "Handwerk", "icon": "/static/res/img/crafting/Handwerk.png", "id": 0, "available": True, "link": None}


	# get all used table instances from db in alpabetical order
	@staticmethod
	def getTables():
		return Tinker.objects.filter(recipe__isnull=False).distinct().order_by("name")

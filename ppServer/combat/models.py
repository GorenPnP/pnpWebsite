import os, re
from datetime import date

from django.conf import settings
from django.db import models
from django.db.models import Max, Sum, Subquery, OuterRef, F, Q, Exists, Value, Q, Value, Case, When
from django.db.models.functions import Coalesce, Concat
from django.core.validators import MaxValueValidator, MinValueValidator
from django.core.exceptions import ValidationError
from django.forms.models import model_to_dict

from django_resized import ResizedImageField
from PIL import Image as PilImage

from character.models import Spieler
from crafting.models import Profile
from ppServer.settings import STATIC_ROOT, STATIC_URL
from shop.models import Tinker


DefaultPlayerStats = {
	"sprite": f"{STATIC_URL}combat/img/char_skin_front.png",
	"speed": 4,
	"hp": 10,
	"defense": 0,
	"weapons": {
		"n": {"accuracy": 90.0, "damage": 7.0, "crit_chance": 0.0, "crit_damage": 0.0, "min_range": 0, "max_range": 1},
		"f": {"accuracy": 95.0, "damage": 5.0, "crit_chance": 0.0, "crit_damage": 0.0, "min_range": 1, "max_range": 5},
		"m": {"accuracy": 99.0, "damage": 0.0, "crit_chance": 0.0, "crit_damage": 0.0, "min_range": 0, "max_range": 3},
	},
}


class Weapon(models.Model):
	class Meta:
		verbose_name = "Waffe/Waffenteil"
		verbose_name_plural = "Waffen/Waffenteile"
		ordering = ["type", "weapon_part", "item"]

	AttackType = [
		("f", "Fernkampf"),
		("n", "Nahkampf"),
		("m", "Magie"),
	]
	ItemType = [
		("a", "komplette Waffe"),
		("v", "Lauf/Vorderteil"),
		("b", "Verbindungsstück"),
		("g", "Griff"),
	]

	name = models.CharField(default="", blank=True, help_text="Optionaler Name")

	item = models.ForeignKey(Tinker, on_delete=models.CASCADE, null=True, blank=True, help_text="kann leer bleiben, um Gegnern Waffen zu definieren")
	type = models.CharField(max_length=1, choices=AttackType)
	weapon_part = models.CharField(max_length=1, choices=ItemType)

	accuracy = models.FloatField(default=0.0, help_text="in %")
	damage = models.FloatField(default=0.0)
	crit_chance = models.FloatField(default=0.0, help_text="in %")
	crit_damage = models.FloatField(default=0.0, help_text="in %")

	min_range = models.PositiveSmallIntegerField(default=1, help_text="in Feldern")
	max_range = models.PositiveSmallIntegerField(default=1, help_text="in Feldern")

	munition = models.ManyToManyField(Tinker, blank=True, related_name="munition")

	def __str__(self):
		return self.name or f'{self.get_type_display()} {self.get_weapon_part_display()} "{self.item.name if self.item else "Spieler"}"'

	def toDict(self):
		fields = [
			"name", "accuracy", "damage", "crit_chance", "crit_damage",
		]
		return {
			**{field: self.__dict__[field] for field in fields},
			"type": self.get_type_display(),
			"weapon_part": self.get_weapon_part_display(),
			"munition": [item.toDict() for item in self.munition.all()]
		}


class RegionEnemy(models.Model):
	class Meta:
		unique_together = ["region", "enemy"]
		ordering = ["region", "enemy"]

	region = models.ForeignKey("Region", on_delete=models.CASCADE)
	enemy = models.ForeignKey("Enemy", on_delete=models.CASCADE)

	num = models.PositiveSmallIntegerField(default=1, validators=[MinValueValidator(1)])

	def __str__(self):
		return f"{self.num}x {self.enemy}"


class Region(models.Model):
	class Meta:
		verbose_name = "Region"
		verbose_name_plural = "Regionen"
		# ordering = ["name"]

	GRID_SIZE = 10
	def init_grid():
		wall = CellType.objects.filter(obstacle=True).values_list("pk", flat=True).first()
		empty = CellType.objects.values_list("pk", flat=True).first()

		return [wall if
		  i % Region.GRID_SIZE in [0, Region.GRID_SIZE-1] or	# left and right walls
		  i < Region.GRID_SIZE or								# top wall
		  i > Region.GRID_SIZE **2 - Region.GRID_SIZE 			# bottom wall
		else empty for i in range(Region.GRID_SIZE **2)]

	name = models.CharField(max_length=128, blank=False, unique=True, default="")

	grid = models.JSONField(default=init_grid, null=False, help_text="List of CellType.pks with length of Region.GRID_SIZE **2")
	cell_types = models.ManyToManyField("CellType", through="RegionalSprite")

	enemies = models.ManyToManyField("Enemy", through=RegionEnemy, blank=True)

	def __str__(self):
		return "Region {}".format(self.name)


class CellType(models.Model):
	class Meta:
		ordering = ["obstacle", "spawn", "enemy_spawn", "exit", "is_default_sprite", "use_default_sprite"]
		unique_together = ["obstacle", "spawn", "enemy_spawn", "exit"]
		constraints = [
			models.UniqueConstraint(fields=["is_default_sprite"], condition=Q(is_default_sprite=True), name="unique_default_sprite")
		]

	name = models.CharField(max_length=128, blank=False, unique=True)

	obstacle = models.BooleanField(default=False)
	spawn = models.BooleanField(default=False)
	enemy_spawn = models.BooleanField(default=False)
	exit = models.BooleanField(default=False)

	is_default_sprite = models.BooleanField(default=False)
	use_default_sprite = models.BooleanField(default=True)

	class SpriteManager(models.Manager):

		def annotate_sprite(self, region: Region):
			""" annotates with sprite of Region (as sprite = ResizedImageField | None) """

			return self.annotate(
				sprite_subpath = Subquery(RegionalSprite.objects.filter(region=region, type=OuterRef("pk")).values_list("sprite")[:1], output_field=models.CharField()),
				sprite = Case(When(sprite_subpath=None, then=None), default=Concat(Value(settings.MEDIA_URL), 'sprite_subpath'), output_field=models.CharField()),
			)
	objects = SpriteManager()

	def __str__(self):
		return "CellType " + self.name


class RegionalSprite(models.Model):
	class Meta:
		ordering = ["region", "type"]
		unique_together = ["region", "type"]

	def upload_sprite_to(instance, filename):
		return f"combat/regional_sprites/{filename}"

	region = models.ForeignKey(Region, on_delete=models.CASCADE)
	type = models.ForeignKey(CellType, on_delete=models.CASCADE)

	sprite = ResizedImageField(size=[64, 64], upload_to=upload_sprite_to)

	def __str__(self):
		return f"Sprite {self.type} von {self.region}"

	def toDict(self):
		return {
			# "region": self.region
			"type": self.type,
			"sprite": self.sprite.url,
		}


class Potion(models.Model):
	class Meta:
		verbose_name = "Trank"
		verbose_name_plural = "Tränke"
		ordering = ["item"]

	TargetEnum = [
		("s", "Spieler"),
		("f", "Fernkampf"),
	]

	item = models.OneToOneField(Tinker, on_delete=models.CASCADE)
	use_on = models.CharField(max_length=1, choices=TargetEnum, default=TargetEnum[0][0])

	def __str__(self):
		return f"Trank {self.item.name}"


class EnemyLoot(models.Model):
	class Meta:
		verbose_name = "Loot"
		verbose_name_plural = "Loot"

	enemy = models.ForeignKey("Enemy", on_delete=models.CASCADE)
	item = models.ForeignKey(Tinker, on_delete=models.CASCADE)

	num = models.PositiveSmallIntegerField(default=1, validators=[MinValueValidator(1)])
	chance = models.FloatField(default=10.0, validators=[MinValueValidator(0.0), MaxValueValidator(100.0)], help_text="in %")


class Enemy(models.Model):
	class Meta:
		verbose_name = "Gegner"
		verbose_name_plural = "Gegner"
		ordering = ["difficulty", "name"]

	def upload_sprite_to(instance, filename):
		return f"combat/enemy_type/{filename}"

	name = models.CharField(max_length=64, unique=True)
	sprite = ResizedImageField(size=[64, 64], upload_to=upload_sprite_to)

	difficulty = models.PositiveSmallIntegerField(default=1)
	speed = models.PositiveSmallIntegerField(default=4)
	hp = models.PositiveSmallIntegerField(default=20)
	defense = models.PositiveSmallIntegerField(default=0)

	weapons = models.ManyToManyField(Weapon)
	loot = models.ManyToManyField(Tinker, through=EnemyLoot, blank=True)

	def __str__(self):
		return f"Gegner {self.name}"
	
	def toDict(self):
		fields = [
			"name",
			"difficulty",
			"speed",
			"hp",
			"defense",
		]
		return {
			**{field: self.__dict__[field] for field in fields},
			"sprite": self.sprite.url,
			"loot": [{"num": loot.num, "chance": loot.chance, "item": loot.item.toDict()} for loot in self.enemyloot_set.all()],
			"weapons": {d["type"]: d for d in self.weapons\
			   .values("type")\
			   .annotate(
				   accuracy = Coalesce(Sum("accuracy"), 0.0),
				   damage = Coalesce(Sum("damage"), 0.0),
				   crit_chance = Coalesce(Sum("crit_chance"), 0.0),
				   crit_damage = Coalesce(Sum("crit_damage"), 0.0),
				   min_range = Coalesce(Sum("min_range"), -1),
				   max_range = Coalesce(Sum("max_range"), -1),
				)
			},
		}
	

# class PlayerStatBoost(models.Model):

# 	class Meta:
# 		ordering = ["type", "item"]

# 	ItemType = [
# 		("r", "Rüstung"),
# 		("f", "Fernkampf-Waffe"),
# 		("fv", "Fernkampf-Lauf"),
# 		("fg", "Fernkampf-Griff"),
# 		("v", "Verbindungsstück"),
# 		("n", "Nahkampfwaffe"),
# 		("nv", "Nahkampf-Vorderteil"),
# 		("ng", "Nahkampf-Griff"),
# 		("m", "Magiewaffe")
# 	]

# 	item = models.OneToOneField(Tinker, on_delete=models.CASCADE)
# 	type = models.CharField(max_length=2, choices=ItemType)

# 	speed = models.SmallIntegerField(default=0)
# 	hp = models.SmallIntegerField(default=0)
# 	defense = models.SmallIntegerField(default=0)
# 	damage_n = models.SmallIntegerField(default=0)
# 	damage_f = models.SmallIntegerField(default=0)
# 	damage_ma = models.SmallIntegerField(default=0)

	# def __str__(self):
	# 	return f"Player-Boost {self.item.name}"

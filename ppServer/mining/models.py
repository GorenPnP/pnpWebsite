import json

from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _

from PIL import Image as PilImage

from shop.models import Tinker

def validate_not_zero(value):
    if value == 0:
        raise ValidationError( _('%(value)s is zero'), params={'value': value})

class Region(models.Model):
	class Meta:
		verbose_name = "Region"
		verbose_name_plural = "Regionen"
		ordering = ["name"]

	name = models.CharField(max_length=200, unique=True)


	def __str__(self):
		return "Region {}".format(self.name)

	def get_field(self, index=0):
		layer = Layer.objects.get(region=self, index=index)
		if not layer: return [[]]

		material_ids_2D = layer.field

		all_materials = {} # {id: material}
		for material in Material.objects.all():
			all_materials[material.id] = material

		for row in material_ids_2D:
			for cell in row:
				cell = all_materials[cell] if cell in all_materials.keys() else None

		return material_ids_2D


class Layer(models.Model):
	class Meta:
		verbose_name = "Layer"
		verbose_name_plural = "Layers"

		unique_together = ["region", "index"]
		ordering = ["region", "index"]

	region = models.ForeignKey(Region, on_delete=models.CASCADE)
	index = models.SmallIntegerField(validators=[MinValueValidator(-100), MaxValueValidator(100)])

	name = models.CharField(max_length=200)
	field = models.JSONField(default=list)

	is_collidable = models.BooleanField(default=True)
	is_mineable = models.BooleanField(default=True)

	def __str__(self):
		return "Layer {} ({}) of {}".format(self.index, self.name, self.region.name)



class Material(models.Model):
	class Meta:
		verbose_name = "Material"
		verbose_name_plural = "Materialien"

	name = models.CharField(max_length=200)
	icon = models.ImageField(null=False, blank=False)
	
	rigidity = models.PositiveIntegerField(default=10, null=False, blank=False)
	tier = models.PositiveIntegerField(default=0, null=False, blank=False)

	def __str__(self):
		return "{}".format(self.name)

	# resize icon
	def save(self, *args, **kwargs):
		MAX_SIZE = 64

		super().save(*args, **kwargs)

		# proceed only if an image exists
		if not self.icon or not self.icon.path: return

		icon = PilImage.open(self.icon.path)

		# is smaller, leave it
		if icon.height <= MAX_SIZE and icon.width <= MAX_SIZE:
			return

		# resize, longest is MAX_SIZE, scale the other accordingly while maintaining ratio
		new_width = MAX_SIZE if icon.width >= icon.height else icon.width * MAX_SIZE // icon.height
		new_height = MAX_SIZE if icon.width <= icon.height else icon.height * MAX_SIZE // icon.width

		icon.thumbnail((new_width, new_height), PilImage.BILINEAR)
		icon.save(self.icon.path, "png")

class MaterialDrop(models.Model):
	item = models.ForeignKey(Tinker, on_delete=models.CASCADE, blank=False, null=True)
	amount = models.TextField(default="[1]")
	material = models.ForeignKey(Material, on_delete=models.CASCADE)

class MaterialGroup(models.Model):

	class Meta:
		verbose_name = "Materialgruppe"
		verbose_name_plural = "Materialgruppen"

		ordering = ["name"]

	name = models.CharField(max_length=200)
	materials = models.ManyToManyField(Material)

	def __str__(self):
		return "Materialgruppe {}".format(self.name)
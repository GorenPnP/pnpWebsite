from django.db.models.signals import post_save, pre_save, post_init
from django.dispatch import receiver

from .models import Modifier, ShopCategory, Tinker
from . import enums


@receiver(post_save, sender=Modifier)
def populate_categories(sender, *args, **kwargs):
    allCategories = [k.kategorie for k in ShopCategory.objects.all()]

    for char, _ in enums.category_enum:
        if not char in allCategories:
            ShopCategory.objects.create(kategorie=char)

@receiver(post_init, sender=Tinker)
def add_minecraft_mod_id(sender, instance, **kwargs):
    
    if (not instance.minecraft_mod_id):
        instance.minecraft_mod_id = instance.name.lower().replace(" ", "_").replace("-", "_").replace("/", "_")
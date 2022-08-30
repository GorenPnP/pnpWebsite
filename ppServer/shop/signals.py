from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Modifier, ShopCategory
from . import enums

@receiver(post_save, sender=Modifier)
def populate_categories(sender, *args, **kwargs):
    allCategories = [k.kategorie for k in ShopCategory.objects.all()]
    print(allCategories)

    for char, _ in enums.category_enum:
        if not char in allCategories:
            ShopCategory.objects.create(kategorie=char)

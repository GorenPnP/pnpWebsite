from django.contrib import admin
from django.utils.html import format_html

from .models import *


class ProfileAdmin(admin.ModelAdmin):
    list_display = ["owner", "name", "restricted", "craftingTime"]


class InventoryAdmin(admin.ModelAdmin):
    list_display = ["char", "item", "num"]
    search_fields = ("char__name", "item__name")


class IngredientInLineAdmin(admin.TabularInline):
    model = Ingredient
    extra = 1
    fk_name = "recipe"


class ProductInLineAdmin(admin.TabularInline):
    model = Product
    extra = 1
    fk_name = "recipe"


class SpezialInLineAdmin(admin.TabularInline):
    model = Recipe.spezial.through
    extra = 1


class WissenInLineAdmin(admin.TabularInline):
    model = Recipe.wissen.through
    extra = 1


class RecipeAdmin(admin.ModelAdmin):

    list_display = ('icons_produkte', 'produkte', 'icons_zutaten', 'zutaten', 'table', 'duration', 'fertigkeiten')
    list_display_links = ('icons_produkte', 'produkte')
    search_fields = ('product__item__name', )

    exclude = ["wissen", "spezial"]

    inlines = [SpezialInLineAdmin, WissenInLineAdmin, IngredientInLineAdmin, ProductInLineAdmin]

    def icons_produkte(self, obj):
        html = format_html("".join(['<img src="{0}" style="max-width: 32px; max-height:32px;" />'.format(p.item.getIconUrl()) for p in obj.product_set.all()]))
        return html if html else "-"

    def produkte(self, obj):
        return ", ".join([i.item.name for i in obj.product_set.all()])

    def icons_zutaten(self, obj):
        html = format_html("".join(['<img src="{0}" style="max-width: 32px; max-height:32px;" />'.format(p.item.getIconUrl()) for p in obj.ingredient_set.all()]))
        return html if html else "-"

    def zutaten(self, obj):
        ingredients = ", ".join([i.item.name for i in obj.ingredient_set.all()])
        return ingredients if ingredients else "-"

    def fertigkeiten(self, obj):
        ferts = ", ".join([e.titel for e in obj.spezial.all()] + [e.titel for e in obj.wissen.all()])
        return ferts if ferts else "-"



admin.site.register(Profile, ProfileAdmin)
admin.site.register(InventoryItem, InventoryAdmin)
admin.site.register(Recipe, RecipeAdmin)

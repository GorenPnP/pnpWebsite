from django.contrib import admin
from django.utils.html import format_html

from .models import *


class ProfileAdmin(admin.ModelAdmin):
    list_display = ["owner", "name", "restricted", "craftingTime"]


class InventoryAdmin(admin.ModelAdmin):
    list_display = ["char", "item", "num"]


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


class MaterialDropInLineAdmin(admin.TabularInline):
    model = MaterialDrop
    extra = 1


class MaterialInLineAdmin(admin.TabularInline):
    model = Material
    exclude = ["tools"]
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


class MaterialAdmin(admin.ModelAdmin):
    list_display = ('_icon', 'name', 'region', 'rigidity', 'spawn_chance', 'second_spawn_chance', '_drops')
    list_display_links = ('_icon', 'name')
    search_fields = ('name', 'region')

    exclude = ('tools', )

    inlines = [MaterialDropInLineAdmin]

    def _icon(self, obj):
        html = format_html('<img src="{0}" style="max-width: 32px; max-height:32px;" />'.format(obj.icon.url))
        return html if html else "-"

    def _drops(self, obj):
        return ", ".join([drop.item.name for drop in MaterialDrop.objects.filter(material=obj)])


class RegionAdmin(admin.ModelAdmin):
    list_display = ('name', 'vorkommen')

    inlines = [MaterialInLineAdmin]

    def vorkommen(self, obj):
        return ", ".join([m.name for m in sorted(Material.objects.filter(region=obj), key=lambda material: material.name)])


admin.site.register(Profile, ProfileAdmin)
admin.site.register(InventoryItem, InventoryAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Material, MaterialAdmin)
admin.site.register(Region, RegionAdmin)

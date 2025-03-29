from typing import Any
from django.contrib import admin
from django.db.models import OuterRef
from django.db.models.query import QuerySet
from django.http import HttpRequest
from django.utils.html import format_html

from ppServer.utils import ConcatSubquery

from .models import *


class ProfileAdmin(admin.ModelAdmin):
    list_display = ["owner", "name", "restricted", "miningTime", "craftingTime"]

    def get_queryset(self, request: HttpRequest) -> QuerySet[Any]:
        return super().get_queryset(request).prefetch_related("owner")


class InventoryAdmin(admin.ModelAdmin):
    list_display = ["char", "item", "num"]
    search_fields = ("char__name", "item__name")

    def get_queryset(self, request: HttpRequest) -> QuerySet[Any]:
        return super().get_queryset(request).prefetch_related("char", "item")


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
    list_editable = ('duration',)

    exclude = ["wissen", "spezial"]

    inlines = [SpezialInLineAdmin, WissenInLineAdmin, IngredientInLineAdmin, ProductInLineAdmin]

    def icons_produkte(self, obj):
        html = format_html("".join(['<img src="{0}" style="max-width: 32px; max-height:32px;" />'.format(p.item.getIconUrl()) for p in obj.product_set.all()]))
        return html or self.get_empty_value_display()

    def produkte(self, obj):
        return obj.produktenames or self.get_empty_value_display()

    def icons_zutaten(self, obj):
        html = format_html("".join(['<img src="{0}" style="max-width: 32px; max-height:32px;" />'.format(p.item.getIconUrl()) for p in obj.ingredient_set.all()]))
        return html or self.get_empty_value_display()

    def zutaten(self, obj):
        return obj.zutatennames or self.get_empty_value_display()

    def fertigkeiten(self, obj):
        separator = ", " if obj.spezialnames and obj.wissennames else ""
        return separator.join([obj.spezialnames, obj.wissennames]) or self.get_empty_value_display()
    
    def get_queryset(self, request: HttpRequest) -> QuerySet[Any]:
        return super().get_queryset(request).prefetch_related("ingredient_set__item", "product_set__item", "table").annotate(
            zutatennames = ConcatSubquery(Ingredient.objects.prefetch_related("item").filter(recipe=OuterRef("id")).values("item__name"), ", "),
            produktenames = ConcatSubquery(Product.objects.prefetch_related("item").filter(recipe=OuterRef("id")).values("item__name"), ", "),
            spezialnames = ConcatSubquery(Spezialfertigkeit.objects.filter(recipe=OuterRef("id")).values("titel"), ", "),
            wissennames = ConcatSubquery(Wissensfertigkeit.objects.filter(recipe=OuterRef("id")).values("titel"), ", "),
        )


class RegionBlockChanceInLineAdmin(admin.TabularInline):
    model = BlockChance
    fields = ['chance', 'block']

    extra = 3

class RegionAdmin(admin.ModelAdmin):

    list_display = ('_icon', 'name')
    list_display_links = ('_icon', 'name')
    search_fields = ('name', )

    fields = ["icon", "name", "allowed_profiles"]
    inlines = [RegionBlockChanceInLineAdmin]

    def _icon(self, obj):
        return format_html('<img src="{0}" style="max-width: 32px; max-height:32px;" />'.format(obj.icon.url)) if obj.icon else self.get_empty_value_display()


class BlockDropInLineAdmin(admin.TabularInline):
    model = Drop
    fields = ["chance", "item"]

    extra = 3

class BlockAdmin(admin.ModelAdmin):

    list_display = ('_icon', 'name', 'hardness', 'effective_pick', 'effective_axe', 'effective_shovel')
    list_display_links = ('_icon', 'name')
    list_editable = ['effective_pick', 'effective_axe', 'effective_shovel']
    search_fields = ('name', )

    fields = ["icon", "name", 'hardness', 'effective_pick', 'effective_axe', 'effective_shovel']
    inlines = [BlockDropInLineAdmin]

    def _icon(self, obj):
        return format_html('<img src="{0}" style="max-width: 32px; max-height:32px;" />'.format(obj.icon.url)) if obj.icon else self.get_empty_value_display()

class ToolAdmin(admin.ModelAdmin):

    list_display = ('_icon', 'name', 'speed', 'is_pick', 'is_axe', 'is_shovel')
    list_display_links = ('_icon', 'name')
    list_editable = ['is_pick', 'is_axe', 'is_shovel']
    search_fields = ('item__name', )

    fields = ["item", "speed", 'is_pick', 'is_axe', 'is_shovel']

    def _icon(self, obj):
        return format_html('<img src="{0}" style="max-width: 32px; max-height:32px;" />'.format(obj.item.icon.url)) if obj.item and obj.item.icon else self.get_empty_value_display()

    def name(self, obj):
        return obj.item.name if obj.item else self.get_empty_value_display()



admin.site.register(Profile, ProfileAdmin)
admin.site.register(InventoryItem, InventoryAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(RelCrafting)

admin.site.register(Region, RegionAdmin)
admin.site.register(Block, BlockAdmin)
admin.site.register(Tool, ToolAdmin)

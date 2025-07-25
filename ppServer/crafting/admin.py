import locale
from typing import Any

from django.contrib import admin
from django.db.models import OuterRef, F, Q, Subquery
from django.db.models.aggregates import Sum
from django.db.models.functions import Coalesce
from django.db.models.query import QuerySet
from django.http import HttpRequest
from django.utils.html import format_html

from ppServer.utils import ConcatSubquery

from .models import *

class AllowedRegionInLineAdmin(admin.TabularInline):
    model = Region.allowed_profiles.through


class ProfileAdmin(admin.ModelAdmin):
    list_display = ["owner", "name", "restricted", "woobles", "miningTime", "craftingTime", "regions"]

    inlines = [AllowedRegionInLineAdmin]

    def get_queryset(self, request: HttpRequest) -> QuerySet[Any]:
        return super().get_queryset(request).prefetch_related("owner", "region_set")
    
    def regions(self, obj):
        return ", ".join([region.name for region in obj.region_set.all()]) or self.get_empty_value_display()


class InventoryAdmin(admin.ModelAdmin):
    list_display = ["char", "item", "num"]
    search_fields = ("char__name", "item__name")
    list_filter = ("char", "item")

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


class PermanentlyNeedsTinkerInLineAdmin(admin.TabularInline):
    model = Region.permanently_needs.through
    extra = 1


class RecipeAdmin(admin.ModelAdmin):

    list_display = ('icons_produkte', 'produkte', 'icons_zutaten', 'zutaten', 'profitable_flip', 'table', 'duration', 'fertigkeiten')
    list_display_links = ('icons_produkte', 'produkte')
    search_fields = ('product__item__name', )

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
    
    @admin.display(ordering="profitable_flip", description="Flip (Produktverkauf - Zutatenkauf)")
    def profitable_flip(self, obj):
        locale.setlocale(locale.LC_NUMERIC, "de_DE.utf8")
        return format_html(f"<b>{obj.profitable_flip:+n}</b><small> = {obj.product_yield:n} - {obj.ingredient_cost:n}</small>")

    def get_queryset(self, request: HttpRequest) -> QuerySet[Any]:
        ingredient_cost_subquery = Ingredient.objects\
            .annotate(
                cost = F("num") * F("item__wooble_buy_price"),
            ).filter(recipe=OuterRef('pk')).values('recipe__pk')\
            .annotate(
                total_cost=Sum('cost'),
            ).values('total_cost')[:1]
        
        product_yield_subquery = Product.objects\
            .annotate(
                cost = F("num") * F("item__wooble_sell_price"),
            ).filter(recipe=OuterRef('pk')).values('recipe__pk')\
            .annotate(
                total_cost=Sum('cost'),
            ).values('total_cost')[:1]

        return super().get_queryset(request).prefetch_related("ingredient_set__item", "product_set__item", "table").annotate(
            zutatennames = ConcatSubquery(Ingredient.objects.prefetch_related("item").filter(recipe=OuterRef("id")).values("item__name"), ", "),
            produktenames = ConcatSubquery(Product.objects.prefetch_related("item").filter(recipe=OuterRef("id")).values("item__name"), ", "),
            spezialnames = ConcatSubquery(Spezialfertigkeit.objects.filter(recipe=OuterRef("id")).values("titel"), ", "),
            wissennames = ConcatSubquery(Wissensfertigkeit.objects.filter(recipe=OuterRef("id")).values("titel"), ", "),
            ingredient_cost = Coalesce(Subquery(ingredient_cost_subquery), 0.0),
            product_yield = Coalesce(Subquery(product_yield_subquery), 0.0),
            profitable_flip = F("product_yield") - F("ingredient_cost"),
        )


class RelCraftingAdmin(admin.ModelAdmin):
    list_display = ['spieler', 'char', 'profil']
    list_filter = ['profil']

class RegionBlockChanceInLineAdmin(admin.TabularInline):
    model = BlockChance
    fields = ['chance', 'block']

    extra = 3

class RegionAdmin(admin.ModelAdmin):

    list_display = ('_icon', 'name', "wooble_cost")
    list_display_links = ('_icon', 'name')
    search_fields = ('name', )

    fields = ["icon", "name", "wooble_cost", "allowed_profiles"]
    inlines = [PermanentlyNeedsTinkerInLineAdmin, RegionBlockChanceInLineAdmin]

    def _icon(self, obj):
        return format_html('<img src="{0}" style="max-width: 32px; max-height:32px;" />'.format(obj.icon.url)) if obj.icon else self.get_empty_value_display()


class BlockDropInLineAdmin(admin.TabularInline):
    model = Drop
    fields = ["chance", "item"]

    extra = 3

class BlockToolInLineAdmin(admin.TabularInline):
    model = Drop
    fields = ["chance", "item"]

    extra = 3

class BlockAdmin(admin.ModelAdmin):

    list_display = ('_icon', 'name', 'hardness', "_tool_types")
    list_display_links = ('_icon', 'name')
    search_fields = ('name', )

    fields = ["icon", "name", 'hardness', "effective_tool"]
    inlines = [BlockDropInLineAdmin]

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related("effective_tool")

    def _icon(self, obj):
        return format_html('<img src="{0}" style="max-width: 32px; max-height:32px;" />'.format(obj.icon.url)) if obj.icon else self.get_empty_value_display()

    def _tool_types(self, obj):
        return ", ".join(obj.effective_tool.values_list("name", flat=True))


class ToolAdmin(admin.ModelAdmin):

    list_display = ('_icon', 'name', 'speed', "type")
    list_display_links = ('_icon', 'name')
    search_fields = ('item__name', )

    fields = ["item", "speed", "is_type"]

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related("is_type")

    def _icon(self, obj):
        return format_html('<img src="{0}" style="max-width: 32px; max-height:32px;" />'.format(obj.item.icon.url)) if obj.item and obj.item.icon else self.get_empty_value_display()

    def name(self, obj):
        return obj.item.name if obj.item else self.get_empty_value_display()
    
    def type(self, obj):
        return ", ".join(obj.is_type.values_list("name", flat=True))

class MiningPerkAdmin(admin.ModelAdmin):

    list_display = ('effect', '_tool_type', 'beschreibung', '_item', 'region')
    list_filter = ('effect', 'tool_type__name', 'region__name')

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related("item", "tool_type")
    
    def _item(self, obj):
        return format_html('<img src="{}" style="max-width: 32px; max-height:32px;" />{}'.format(obj.item.getIconUrl(), obj.item.name))

    def _tool_type(self, obj):
        return ", ".join(obj.tool_type.values_list("name", flat=True))


admin.site.register(Profile, ProfileAdmin)
admin.site.register(InventoryItem, InventoryAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(RelCrafting, RelCraftingAdmin)

admin.site.register(Region, RegionAdmin)
admin.site.register(Block, BlockAdmin)
admin.site.register(Tool, ToolAdmin)
admin.site.register(MiningPerk, MiningPerkAdmin)
admin.site.register(ToolType)

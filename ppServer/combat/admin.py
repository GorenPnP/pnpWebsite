from django.contrib import admin
from django.utils.html import format_html

from ppServer.utils import ConcatSubquery

from .models import *


class RegionEnemyInLineAdmin(admin.TabularInline):
    model = RegionEnemy

class RegionalSpriteInLineAdmin(admin.TabularInline):
    model = RegionalSprite
    fields = ["type", "sprite"]

class EnemyLootInLineAdmin(admin.TabularInline):
    model = EnemyLoot
    fields = ["num", "chance", "item"]


class RegionAdmin(admin.ModelAdmin):

    list_display = ('name', )
    search_fields = ('name', )

    fields = ["name", "grid"]
    readonly_fields = ["grid"]

    inlines = [RegionalSpriteInLineAdmin, RegionEnemyInLineAdmin]


class CellTypeAdmin(admin.ModelAdmin):

    list_display = ('name', "obstacle", "spawn", "enemy_spawn", "exit", "is_default_sprite", "use_default_sprite")
    list_editable = ["obstacle", "spawn", "enemy_spawn", "exit", "is_default_sprite", "use_default_sprite"]
    search_fields = ('name', )


class PotionAdmin(admin.ModelAdmin):
    list_display = ('_sprite', "_name", "use_on")
    list_display_links = ["_sprite", "_name"]

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related("item")

    def _sprite(self, obj):
        return format_html(f'<img src="{obj.item.icon.url}" style="max-width: 32px; max-height:32px;" />') if obj.item else self.get_empty_value_display()

    def _name(self, obj):
        return obj.item.name


class EnemyAdmin(admin.ModelAdmin):
    list_display = ('_sprite', "name", "difficulty", "_weapons")
    list_display_links = ["_sprite", "name"]

    inlines = [EnemyLootInLineAdmin, RegionEnemyInLineAdmin]

    def _sprite(self, obj):
        return format_html(f'<img src="{obj.sprite.url}" style="max-width: 32px; max-height:32px;" />') if obj.sprite else self.get_empty_value_display()

    def _weapons(self, obj):
        return ", ".join(weapon.__str__() for weapon in obj.weapons.all()) or self.get_empty_value_display()


# class PlayerStatBoostAdmin(admin.ModelAdmin):
#     list_display = ('_sprite', "_name", "type", "_boost", "_munition")
#     list_display_links = ["_sprite", "_name"]

#     def get_queryset(self, request):
#         return super().get_queryset(request).prefetch_related("item").annotate(
#             munition_display = ConcatSubquery(Tinker.objects.filter(id__in=OuterRef("munition__pk")).values("name"), ", ")
#         )

#     def _sprite(self, obj):
#         return format_html(f'<img src="{obj.item.icon.url}" style="max-width: 32px; max-height:32px;" />') if obj.item else self.get_empty_value_display()

#     def _name(self, obj):
#         return obj.item.name
    
#     def _boost(self, obj):
#         fields = [
#             "speed",
# 	        "hp",
# 	        "defense",
# 	        "damage_n",
# 	        "damage_f",
# 	        "damage_ma",
#         ]
#         return ", ".join(f"{obj.__dict__[field]:+n} {field}" for field in fields if obj.__dict__[field])
    
#     def _munition(self, obj):
#         return obj.munition_display or self.get_empty_value_display()


class WeaponAdmin(admin.ModelAdmin):
    list_display = ('_icon', "type", "weapon_part", "accuracy", "damage", "crit_chance", "crit_damage", "_range", "_munition")
    list_display_links = ["_icon", "type"]

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related("item").annotate(
            munition_display = ConcatSubquery(Tinker.objects.filter(id__in=OuterRef("munition__pk")).values("name"), ", ")
        )

    def _icon(self, obj):
        return format_html(f'<img src="{obj.item.icon.url}" style="max-width: 32px; max-height:32px;" />') if obj.item else self.get_empty_value_display()

    @admin.display(ordering="max_range")
    def _range(self, obj):
        return f"{obj.min_range} - {obj.max_range} Felder"

    def _munition(self, obj):
        return obj.munition_display or self.get_empty_value_display()


class RelWeaponsInlineAdmin(admin.TabularInline):
    model = RelWeapon
    fields = ["weapon"]
    extra = 1
class PlayerStatsAdmin(admin.ModelAdmin):
    list_display = ("char", "profil", "speed", "hp", "defense")
    list_filter = ["profil", "char"]
    inlines = [RelWeaponsInlineAdmin]

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related("char", "profil")


admin.site.register(Region, RegionAdmin)
admin.site.register(CellType, CellTypeAdmin)
admin.site.register(Potion, PotionAdmin)
admin.site.register(Enemy, EnemyAdmin)
# admin.site.register(PlayerStatBoost, PlayerStatBoostAdmin)
admin.site.register(PlayerStats, PlayerStatsAdmin)
admin.site.register(Weapon, WeaponAdmin)
from django.db.models.query import QuerySet
from django.db.models import Exists, OuterRef

from .models import Recipe, MiningPerk


# queryset may contain either ingredients or products of recipes
def construct_recipes(recipe_qs: QuerySet[Recipe], inventory, table_id: int = None):
	if table_id is not None:
		# filter recipes by table. Recipe without table is represented by table_id=0, but need to query with table_id=None
		recipe_qs = recipe_qs.prefetch_related("table__item").filter(table__item__id=None if table_id == 0 else table_id)

	recipes = []
	for recipe in recipe_qs:

		recipe = {
			"id": recipe.id,
			"ingredients": [{"num": i.num, "own": inventory[i.item.id] if i.item.id in inventory.keys() else 0, "icon": i.item.getIconUrl(), "name": i.item.name} for i in recipe.ingredient_set.all()],
			"products": [{"num": p.num, "icon": p.item.getIconUrl(), "name": p.item.name, "id": p.item.id} for p in recipe.product_set.all()],
			"table": {"icon": recipe.table.item.getIconUrl(), "name": recipe.table.item.name} if recipe.table else Recipe.getHandwerk(),
			"locked": recipe.table.item.id not in inventory.keys() if recipe.table else False,
			"produces_perk": recipe.produces_perk,
			"is_fav": recipe.is_fav,
		}
		recipes.append(recipe)

	return recipes

from crafting.models import Recipe


# queryset may contain either ingredients or products of recipes
def construct_recipes(queryset, inventory, rel):
	recipes = []
	recipe_ids = []
	for q in queryset:
		recipe = q.recipe

		# prevent duplicates
		if recipe.id in recipe_ids: continue
		recipe_ids.append(recipe.id)

		ingredients = recipe.ingredient_set.all()
		products = recipe.product_set.all()

		# restrict only to recipes that need ingredients, IF restricted
		if rel.profil.restricted and not ingredients.exists():
			continue

		recipe = {
			"id": recipe.id,
			"ingredients": [{"num": i.num, "own": inventory[i.item.id] if i.item.id in inventory.keys() else 0, "icon": i.item.getIconUrl(), "name": i.item.name} for i in ingredients],
			"products": [{"num": p.num, "icon": p.item.getIconUrl(), "name": p.item.name, "id": p.item.id} for p in products],
			"table": {"icon": recipe.table.getIconUrl(), "name": recipe.table.name} if recipe.table else Recipe.getHandwerk(),
			"locked": recipe.table.id not in inventory.keys() if recipe.table else False
		}
		recipes.append(recipe)

	return recipes


# inventory of a profile, restricted = profile.restricted, id = id of table
def get_recipes_of_table(inventory, restricted, id):

	# get all recipes that need the table with this id
	recipes = []
	for r in Recipe.objects.prefetch_related("ingredient_set__item", "product_set__item").filter(table__id=id if id else None):		# without table is represented by id=0, but need to query with table=None

		ingredients = r.ingredient_set.all()
		if restricted and not ingredients.exists(): continue

		products = r.product_set.all()

		recipe = {
			"id": r.id,
			"ingredients": [{"num": i.num, "own": inventory[i.item.id] if i.item.id in inventory.keys() else 0, "icon": i.item.getIconUrl(), "name": i.item.name} for i in ingredients],
			"products": [{"num": n.num, "icon": n.item.getIconUrl(), "name": n.item.name, "id": n.item.id} for n in products],
			"locked": id not in inventory.keys() if id else False		# special case again for Handwerk
		}
		recipes.append(recipe)

	return recipes

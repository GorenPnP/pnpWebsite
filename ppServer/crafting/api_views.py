import os, re, zipfile

from django.http.response import FileResponse
from django.views import View

from ppServer.settings import STATIC_ROOT

from .models import *


TICKS_PER_SECOND = 20
HANDWERK_ID = Tinker.getIdOdMod() + ":handwerk"

def makedirs(path):
    try:
        os.makedirs(path)
    except FileExistsError:
        # directory already exists
        pass    



class GetMinecraftRecipesView(View):

    def get(self, *args, **kwargs):
        timeFactor = int(self.request.GET.get("second_multiplier", TICKS_PER_SECOND))

        # prepare the scene
        os.chdir(STATIC_ROOT)
        makedirs("minecraft_recipes/recipes")
        os.chdir("minecraft_recipes")

        if os.path.exists("recipes.zip"):
            os.remove("recipes.zip")

        # init zip archive. add all json files of recipes
        with zipfile.ZipFile("recipes.zip", mode="w", compression=zipfile.ZIP_DEFLATED) as zip_file:

            for i, recipe in enumerate(Recipe.objects.all()):

                productName = re.sub('.*:', '', recipe.product_set.first().item.getMinecraftModId().replace("/", "_"))
                tableName = re.sub('.*:', '', recipe.table.getMinecraftModId() if recipe.table else HANDWERK_ID)

                dirPath = "recipes/{}".format(tableName)
                filename = "{}/{}-{}.json".format(dirPath, i, productName)
                
                makedirs(dirPath)
                with open(filename, "w") as file:
                
                    jsonRecipe = {
                        "type": recipe.table.getMinecraftModId() if recipe.table else HANDWERK_ID,
                        "ingredients": [{"item": p.item.getMinecraftModId(), "count": int(p.num)} for p in recipe.ingredient_set.all()],
                        "outputs": [{"item": p.item.getMinecraftModId(), "count": int(p.num)} for p in recipe.product_set.all()],
                        "processingTime": recipe.duration.seconds * timeFactor
                    }

                    file.write(json.dumps(jsonRecipe, indent=2))

                zip_file.write(filename)


        return FileResponse(open('recipes.zip', 'rb'), filename="recipes.zip", as_attachment=True)

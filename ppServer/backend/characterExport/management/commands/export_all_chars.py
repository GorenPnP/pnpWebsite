import os, zipfile

from django.core.management.base import BaseCommand

from ppServer.settings import STATIC_ROOT
from character.models import Charakter

from characterExport.export import CharakterExporter


class Command(BaseCommand):
    help = "Generates a <char-name>.xlsx for every character and zips them"

    def handle(self, *args, **options):
        import glob
        ZIP_FILENAME = "characters.zip"

        full_path = [STATIC_ROOT, "character_export", "characters"]

        # prepare the scene
        os.chdir(full_path[0])
        if not os.path.exists(full_path[1]):
            os.makedirs(full_path[1])
        os.chdir(full_path[1])

        if not os.path.exists(full_path[2]):
            os.makedirs(full_path[2])

        if os.path.exists(ZIP_FILENAME):
            os.remove(ZIP_FILENAME)



        # init zip archive. add all json files of recipes
        with zipfile.ZipFile(ZIP_FILENAME, mode="w", compression=zipfile.ZIP_DEFLATED) as zip_file:

            for char in Charakter.objects.all().prefetch_related("eigentümer"):
                file_response = CharakterExporter(char).export()

                owner = char.eigentümer.__str__() if char.eigentümer is not None else 'NO_OWNER'
                name = (char.name or 'NO_NAME').replace('"', '').replace("'", '')
                filename = f"{owner.replace('/', '_').replace('.', '_')} - {name.replace('/', '_').replace('.', '_')}.xlsx"
                path = os.path.join(full_path[2], filename)

                with open(path, "wb") as file:
                    file.write(file_response.content)

                zip_file.write(path)
                self.stdout.write(self.style.NOTICE(f'Exporting "{filename}"'))

        self.stdout.write(self.style.SUCCESS(f'Successfully generated zip at "{ZIP_FILENAME}"'))

        files = glob.glob(os.path.join(*full_path, '*.xlsx'))
        for f in files:
            try:
                os.remove(f)
            except OSError:
                self.stdout.write(self.style.ERROR(f'Could not delete "{f}"'))
                return
        os.removedirs(full_path[2])

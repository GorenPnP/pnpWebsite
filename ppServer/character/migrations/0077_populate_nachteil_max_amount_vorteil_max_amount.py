# Generated by Django 4.1.7 on 2023-04-16 09:24

from django.db import migrations, models

def populate_max_amount(apps, schema_editor):
    Vorteil = apps.get_model('character', 'Vorteil')
    Nachteil = apps.get_model('character', 'Nachteil')

    vorteile = []
    for teil in Vorteil.objects.filter(titel__in=[
            "Magisches Band", "Meister", "Schutzgeist", "Spezialisiert", "Talentiert", "Immunität", "Resistenz"
        ]):
        teil.max_amount = None
        vorteile.append(teil)
    Vorteil.objects.bulk_update(vorteile, ["max_amount"])

    nachteile = []
    for teil in Nachteil.objects.filter(titel__in=[
            "Allergie", "Angst", "Besessen", "Codex", "Defizit", "Drogenabhängig", "Fanatisch", "Feind",
            "Galaktisches Ziel", "Gespaltene Persönlichkeit", "Rassistisch", "Schwere Allergie", "Unkontrolliert",
            "Verbittert", "Verliebt", "Voreingenommen", "Anfälligkeit"
        ]):
        teil.max_amount = None
        nachteile.append(teil)
    Nachteil.objects.bulk_update(nachteile, ["max_amount"])


class Migration(migrations.Migration):

    dependencies = [
        ('character', '0076_nachteil_max_amount_vorteil_max_amount'),
    ]

    operations = [
        migrations.RunPython(populate_max_amount)
    ]

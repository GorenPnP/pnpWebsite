# Generated by Django 4.2.8 on 2024-01-21 17:11

from django.db import migrations

def combine_sonstige(apps, schema_editor):
    Charakter = apps.get_model('character', 'Charakter')

    chars = []
    for char in Charakter.objects.all():
        fields = [char.sonstige_items, char.sonstiges_alchemie, char.sonstiges_cyberware]
        char.sonstige_items = "\n\n".join([field for field in fields if field])

        chars.append(char)
    Charakter.objects.bulk_update(chars, fields=["sonstige_items"])


class Migration(migrations.Migration):

    dependencies = [
        ('character', '0143_charakter_sonstiges_alchemie_and_more'),
    ]

    operations = [
        migrations.RunPython(combine_sonstige),
        migrations.RemoveField(
            model_name='charakter',
            name='sonstiges_alchemie',
        ),
        migrations.RemoveField(
            model_name='charakter',
            name='sonstiges_cyberware',
        ),
    ]

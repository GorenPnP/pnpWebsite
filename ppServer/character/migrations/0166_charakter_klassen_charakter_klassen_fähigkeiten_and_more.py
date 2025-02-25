# Generated by Django 4.2.8 on 2024-11-01 08:51

from django.db import migrations, models


def set_reduced_rewards_until_klasse_stufe(apps, schema_editor):
    Charakter = apps.get_model('character', 'Charakter')
    Charakter.objects.update(reduced_rewards_until_klasse_stufe=models.F("ep_stufe_in_progress"))

class Migration(migrations.Migration):

    dependencies = [
        ('character', '0165_remove_charakter_persönlichkeit_old'),
    ]

    operations = [
        migrations.AddField(
            model_name='charakter',
            name='klassen',
            field=models.ManyToManyField(blank=True, through='character.RelKlasse', to='character.klasse'),
        ),
        migrations.AddField(
            model_name='charakter',
            name='klassen_fähigkeiten',
            field=models.ManyToManyField(blank=True, through='character.RelKlasseAbility', to='character.klasseability'),
        ),
        migrations.AddField(
            model_name='charakter',
            name='reduced_rewards_until_klasse_stufe',
            field=models.PositiveSmallIntegerField(default=0),
        ),
        migrations.DeleteModel(
            name='RelPersönlichkeit',
        ),
        migrations.RunPython(set_reduced_rewards_until_klasse_stufe),
    ]

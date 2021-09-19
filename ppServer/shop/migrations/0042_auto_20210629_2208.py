# Generated by Django 3.1.5 on 2021-06-29 20:08

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0041_auto_20201111_2045'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='alchemie',
            options={'ordering': ['name'], 'verbose_name': 'Alchemie', 'verbose_name_plural': 'Alchemie'},
        ),
        migrations.AlterModelOptions(
            name='ausrüstung_technik',
            options={'ordering': ['name'], 'verbose_name': 'Ausrüstung/Technik', 'verbose_name_plural': 'Ausrüstung & Technik'},
        ),
        migrations.AlterModelOptions(
            name='einbauten',
            options={'ordering': ['name'], 'verbose_name': 'Einbauten', 'verbose_name_plural': 'Einbauten'},
        ),
        migrations.AlterModelOptions(
            name='fahrzeug',
            options={'ordering': ['name'], 'verbose_name': 'Fahrzeug', 'verbose_name_plural': 'Fahrzeuge'},
        ),
        migrations.AlterModelOptions(
            name='item',
            options={'ordering': ['name'], 'verbose_name': 'Item', 'verbose_name_plural': 'Items'},
        ),
        migrations.AlterModelOptions(
            name='magazin',
            options={'ordering': ['name'], 'verbose_name': 'Magazin', 'verbose_name_plural': 'Magazine'},
        ),
        migrations.AlterModelOptions(
            name='magische_ausrüstung',
            options={'ordering': ['name'], 'verbose_name': 'magische Ausrüstung', 'verbose_name_plural': 'magische Ausrüstung'},
        ),
        migrations.AlterModelOptions(
            name='pfeil_bolzen',
            options={'ordering': ['name'], 'verbose_name': 'Pfeil/Bolzen', 'verbose_name_plural': 'Pfeile & Bolzen'},
        ),
        migrations.AlterModelOptions(
            name='rituale_runen',
            options={'ordering': ['name'], 'verbose_name': 'Ritual/Rune', 'verbose_name_plural': 'Rituale & Runen'},
        ),
        migrations.AlterModelOptions(
            name='rüstungen',
            options={'ordering': ['name'], 'verbose_name': 'Rüstung', 'verbose_name_plural': 'Rüstung'},
        ),
        migrations.AlterModelOptions(
            name='schusswaffen',
            options={'ordering': ['name'], 'verbose_name': 'Schusswaffe', 'verbose_name_plural': 'Schusswaffen'},
        ),
        migrations.AlterModelOptions(
            name='tinker',
            options={'ordering': ['name'], 'verbose_name': 'Für Selbstständige', 'verbose_name_plural': 'Für Selbstständige'},
        ),
        migrations.AlterModelOptions(
            name='waffen_werkzeuge',
            options={'ordering': ['name'], 'verbose_name': 'Waffe/Werkzeug', 'verbose_name_plural': 'Waffen & Werkzeuge'},
        ),
        migrations.AlterModelOptions(
            name='zauber',
            options={'ordering': ['name'], 'verbose_name': 'Zauber', 'verbose_name_plural': 'Zauber'},
        ),
    ]
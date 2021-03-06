# Generated by Django 2.2.13 on 2020-11-11 19:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0040_auto_20201022_2100'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tinker',
            name='kategorie',
            field=models.CharField(choices=[('m', 'Maschinen/Technik'), ('ru', 'Rüstungen/Schilde'), ('c', 'Cyberware'), ('n', 'N.-Waffen'), ('f', 'F.-Waffen'), ('b', 'Bioware'), ('a', 'andere Waffen'), ('w', 'Werkzeuge'), ('ro', 'Rohstoffe/Werkstoffe'), ('k', 'Trankzutaten'), ('t', 'Tränke'), ('z', 'Zauber/Upgrades/Verbesserungen'), ('p', 'Produktionsstätten'), ('u', 'Müll'), ('e', 'Energie')], default='m', max_length=2),
        ),
    ]

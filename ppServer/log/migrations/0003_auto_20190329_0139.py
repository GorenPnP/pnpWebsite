# Generated by Django 2.0.5 on 2019-03-29 00:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('log', '0002_auto_20190126_1916'),
    ]

    operations = [
        migrations.AlterField(
            model_name='log',
            name='art',
            field=models.CharField(choices=[('s', 'Shop'), ('o', 'Sonderangebot'), ('a', 'Attribute'), ('f', 'Fertigkeiten'), ('h', 'HPcp'), ('g', 'mehr Geld'), ('c', 'mehr CP'), ('b', 'mehr EP'), ('p', 'mehr SP'), ('r', 'mehr Rang'), ('e', 'weniger Geld'), ('k', 'weniger SP'), ('n', 'neuer Nachteil'), ('x', 'Nachteil weg'), ('y', 'neuer Vorteil'), ('z', 'Vorteil weg'), ('t', 'Skilltree'), ('m', 'Manaverbrauch abgezogen'), ('v', 'Magie verloren'), ('d', 'Quiz-Punkte für SP')], max_length=1),
        ),
    ]

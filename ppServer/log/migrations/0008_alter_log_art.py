# Generated by Django 4.1.7 on 2023-06-13 19:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('log', '0007_alter_log_options_alter_log_char'),
    ]

    operations = [
        migrations.AlterField(
            model_name='log',
            name='art',
            field=models.CharField(choices=[('s', 'Shop'), ('u', 'Auswertung'), ('i', 'Stufenaufstieg'), ('o', 'Sonderangebot'), ('a', 'Attribute'), ('f', 'Fertigkeiten'), ('h', 'HPcp'), ('g', 'mehr Geld'), ('c', 'mehr CP'), ('b', 'mehr EP'), ('p', 'mehr SP'), ('r', 'mehr Rang'), ('e', 'weniger Geld'), ('k', 'weniger SP'), ('n', 'neuer Nachteil'), ('x', 'Nachteil weg'), ('y', 'neuer Vorteil'), ('z', 'Vorteil weg'), ('t', 'Skilltree'), ('m', 'Manaverbrauch abgezogen'), ('v', 'Magie verloren'), ('d', 'Quiz-Punkte für SP')], max_length=1),
        ),
    ]
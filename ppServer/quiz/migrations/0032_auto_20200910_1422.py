# Generated by Django 2.2.13 on 2020-09-10 12:22

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('quiz', '0031_auto_20200910_1420'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='spielermodule',
            options={'ordering': ['spieler', 'state', 'module'], 'verbose_name': "Spieler's Module", 'verbose_name_plural': "Spieler's Module"},
        ),
    ]

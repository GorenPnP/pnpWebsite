# Generated by Django 3.1.7 on 2022-02-21 18:44

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('character', '0055_auto_20211028_1340'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='gfs',
            options={'ordering': ['titel'], 'verbose_name': 'Gfs/Klasse', 'verbose_name_plural': 'Gfs/Klassen'},
        ),
    ]

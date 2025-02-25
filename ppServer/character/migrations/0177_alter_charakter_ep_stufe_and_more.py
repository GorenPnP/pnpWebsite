# Generated by Django 4.2.8 on 2024-12-20 14:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('character', '0176_gfs_eigenschaften_gfs_eigenschaften_rendered'),
    ]

    operations = [
        migrations.AlterField(
            model_name='charakter',
            name='ep_stufe',
            field=models.PositiveIntegerField(default=1, verbose_name='aktuelle Stufe des Charakters'),
        ),
        migrations.AlterField(
            model_name='charakter',
            name='ep_stufe_in_progress',
            field=models.PositiveIntegerField(default=1, verbose_name='Stufe des Charakters, die noch verteilt werden muss'),
        ),
    ]

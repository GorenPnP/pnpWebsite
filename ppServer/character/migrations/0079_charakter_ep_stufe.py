# Generated by Django 4.1.7 on 2023-05-03 21:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('character', '0078_remove_charakter_eco_remove_charakter_morph_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='charakter',
            name='ep_stufe',
            field=models.PositiveIntegerField(default=0),
        ),
    ]
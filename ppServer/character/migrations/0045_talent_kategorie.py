# Generated by Django 2.2.13 on 2020-08-18 19:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('character', '0044_auto_20200816_2239'),
    ]

    operations = [
        migrations.AddField(
            model_name='talent',
            name='kategorie',
            field=models.CharField(choices=[('k', 'Kampfkunst'), ('g', 'Geistig'), ('m', 'Magisch'), ('a', 'Kampfmagisch'), ('u', 'Support'), ('o', 'Sozial'), ('w', 'Schwächend'), ('p', 'Gameplay')], default='k', max_length=1),
        ),
    ]

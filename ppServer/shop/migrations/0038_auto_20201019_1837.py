# Generated by Django 2.2.13 on 2020-10-19 16:37

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0037_auto_20201019_1831'),
    ]

    operations = [
        migrations.AddField(
            model_name='tinker',
            name='num_product',
            field=models.FloatField(blank=True, default=1, validators=[django.core.validators.MinValueValidator(1e-06)]),
        ),
        migrations.AlterField(
            model_name='tinkerneeds',
            name='num',
            field=models.FloatField(blank=True, default=1, validators=[django.core.validators.MinValueValidator(1e-06)]),
        ),
        migrations.AlterField(
            model_name='tinkerwaste',
            name='num',
            field=models.FloatField(blank=True, default=1, validators=[django.core.validators.MinValueValidator(1e-06)]),
        ),
    ]

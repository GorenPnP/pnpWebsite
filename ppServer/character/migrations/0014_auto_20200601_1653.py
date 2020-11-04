# Generated by Django 2.0.5 on 2020-06-01 14:53

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('character', '0013_auto_20190416_0004'),
    ]

    operations = [
        migrations.AlterField(
            model_name='nachteil',
            name='cp',
            field=models.PositiveIntegerField(default=0, validators=[django.core.validators.MaxValueValidator(1000)]),
        ),
        migrations.AlterField(
            model_name='vorteil',
            name='cp',
            field=models.PositiveIntegerField(default=0, validators=[django.core.validators.MaxValueValidator(1000)]),
        ),
    ]

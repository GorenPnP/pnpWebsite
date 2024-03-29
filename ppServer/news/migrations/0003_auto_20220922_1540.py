# Generated by Django 3.1.7 on 2022-09-22 13:40

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('news', '0002_auto_20220904_2049'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='news',
            options={'ordering': ['-creation', '-importance'], 'verbose_name': 'News', 'verbose_name_plural': 'News'},
        ),
        migrations.AlterField(
            model_name='news',
            name='importance',
            field=models.PositiveSmallIntegerField(default=3, help_text='5 has highest importance, 1 lowest', validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(5)]),
        ),
    ]

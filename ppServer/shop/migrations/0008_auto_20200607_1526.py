# Generated by Django 2.0.5 on 2020-06-07 13:26

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0007_auto_20200607_1442'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sttinker',
            name='herstellungsdauer',
            field=models.DurationField(blank=True, default=datetime.timedelta(0), verbose_name='herstellungsdauer (d:hh:mm)'),
        ),
        migrations.AlterField(
            model_name='tinker',
            name='herstellungsdauer',
            field=models.DurationField(blank=True, default=datetime.timedelta(0), verbose_name='herstellungsdauer (d:hh:mm)'),
        ),
    ]

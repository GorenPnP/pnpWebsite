# Generated by Django 2.2.13 on 2020-09-23 10:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0033_auto_20200815_1925'),
    ]

    operations = [
        migrations.AddField(
            model_name='firma',
            name='price_factor',
            field=models.SmallIntegerField(default=1),
        ),
    ]

# Generated by Django 2.2.13 on 2020-09-18 09:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('character', '0050_auto_20200913_1135'),
    ]

    operations = [
        migrations.AddField(
            model_name='charakter',
            name='larp',
            field=models.BooleanField(default=False),
        ),
    ]

# Generated by Django 2.0.5 on 2019-01-26 18:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('character', '0007_auto_20190126_1306'),
    ]

    operations = [
        migrations.AddField(
            model_name='charakter',
            name='ep',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='charakter',
            name='ep_rang',
            field=models.PositiveIntegerField(default=0),
        ),
    ]

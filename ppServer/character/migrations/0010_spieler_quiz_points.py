# Generated by Django 2.0.5 on 2019-03-13 01:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('character', '0009_auto_20190311_1518'),
    ]

    operations = [
        migrations.AddField(
            model_name='spieler',
            name='quiz_points',
            field=models.PositiveIntegerField(default=0),
        ),
    ]

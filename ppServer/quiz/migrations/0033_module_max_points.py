# Generated by Django 2.2.13 on 2020-09-10 12:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('quiz', '0032_auto_20200910_1422'),
    ]

    operations = [
        migrations.AddField(
            model_name='module',
            name='max_points',
            field=models.FloatField(default=0),
        ),
    ]

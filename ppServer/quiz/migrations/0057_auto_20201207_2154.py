# Generated by Django 2.2.13 on 2020-12-07 20:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('quiz', '0056_auto_20201206_1700'),
    ]

    operations = [
        migrations.AlterField(
            model_name='relquiz',
            name='quiz_points_achieved',
            field=models.FloatField(blank=True, default=0),
        ),
    ]
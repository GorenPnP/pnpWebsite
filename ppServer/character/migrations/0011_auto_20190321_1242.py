# Generated by Django 2.0.5 on 2019-03-21 11:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('character', '0010_spieler_quiz_points'),
    ]

    operations = [
        migrations.AddField(
            model_name='spieler',
            name='quiz_points_achieved',
            field=models.PositiveIntegerField(blank=True, default=0),
        ),
        migrations.AlterField(
            model_name='spieler',
            name='quiz_points',
            field=models.PositiveIntegerField(blank=True, default=0),
        ),
    ]

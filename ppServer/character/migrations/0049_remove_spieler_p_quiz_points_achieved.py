# Generated by Django 2.2.14 on 2020-09-09 17:59

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('character', '0048_merge_20200827_2046'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='spieler',
            name='p_quiz_points_achieved',
        ),
    ]

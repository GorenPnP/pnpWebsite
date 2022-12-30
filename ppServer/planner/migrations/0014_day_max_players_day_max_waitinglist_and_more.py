# Generated by Django 4.1.4 on 2022-12-30 14:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('planner', '0013_rename_users_day_proposals'),
    ]

    operations = [
        migrations.AddField(
            model_name='day',
            name='max_players',
            field=models.PositiveSmallIntegerField(default=4),
        ),
        migrations.AddField(
            model_name='day',
            name='max_waitinglist',
            field=models.PositiveSmallIntegerField(default=2),
        ),
        migrations.AlterField(
            model_name='blockedtime',
            name='name',
            field=models.CharField(default='', max_length=200),
        ),
    ]
# Generated by Django 3.1.7 on 2022-05-03 13:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0042_auto_20210629_2208'),
    ]

    operations = [
        migrations.AddField(
            model_name='zauber',
            name='manaverbrauch',
            field=models.CharField(blank=True, default='', max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='zauber',
            name='astralschaden',
            field=models.CharField(blank=True, default='', max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='zauber',
            name='schaden',
            field=models.CharField(blank=True, default='', max_length=100, null=True),
        ),
    ]
